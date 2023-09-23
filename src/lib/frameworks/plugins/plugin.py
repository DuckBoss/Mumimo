import logging
import pathlib
import threading
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Union

from ....config import Config
from ....constants import LogOutputIdentifiers, PluginCfgFields
from ....exceptions import PluginError
from ....utils import mumble_utils
from ...frameworks.gui.gui import GUIFramework
from ...message_queue import MessageQueue
from .message_relay_definitions import MessageRelayDefinitions
from . import plugin_output_parameters

logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from ....lib.command import Command


class PluginCompileConstants:
    class Status(Enum):
        NONE = 0
        OK = 1
        FAILED = 2

    class Reason(Enum):
        NONE = 0
        COMMAND_EXCLUSIVE = 1
        COMMAND_DISABLED = 2
        PARAMETER_DISABLED = 3
        PARAMETER_INVALID = 4


class ParameterCompileResult:
    def __init__(
        self,
        parameters: Optional[Union[List[str], str]] = None,
        result: Optional[Dict[str, Any]] = None,
        status: PluginCompileConstants.Status = PluginCompileConstants.Status.NONE,
        reason: PluginCompileConstants.Reason = PluginCompileConstants.Reason.NONE,
    ) -> None:
        if isinstance(parameters, str):
            parameters = [parameters]
        self.parameters = parameters
        self.result = result
        self.status = status
        self.reason = reason


class PluginBase(ABC):
    _plugin_name: str = __name__
    _plugin_metadata: Config
    _is_running: bool = False
    _thread_stop_event: threading.Event = threading.Event()
    _command_parameters: Dict[str, List[str]] = {}
    _exclusive_parameters: Dict[str, List[str]] = {}
    _output_message_queue: MessageQueue

    @classmethod
    def makeCommandRegister(cls):
        # Thanks to ninjagecko/Palo for this idea:
        # https://stackoverflow.com/questions/5707589/calling-functions-by-array-index-in-python/5707605#5707605
        registered_cmds = {}

        def register(parameters: Optional[List[str]] = None, parameters_required: bool = False, exclusive_parameters: Optional[List[str]] = None):
            if parameters is None:
                parameters = []
            if exclusive_parameters is None:
                exclusive_parameters = []

            def register_with_parameters(func):
                registered_cmds[func.__name__] = (
                    func,
                    parameters,
                    parameters_required,
                    exclusive_parameters,
                    MessageRelayDefinitions.get_definitions(),
                )
                return func

            return register_with_parameters

        register.all = registered_cmds
        return register

    @property
    def is_running(self):
        return self._is_running

    @property
    def command_parameters(self):
        return self._command_parameters

    @property
    def exclusive_parameters(self):
        return self._exclusive_parameters

    @property
    def plugin_name(self):
        return self._plugin_name

    @property
    def output_message_queue(self):
        return self._output_message_queue

    @property
    def plugin_metadata(self) -> Config:
        return self._plugin_metadata

    def __init__(self, plugin_name: str) -> None:
        super().__init__()
        self._plugin_name = plugin_name
        self._output_message_queue = MessageQueue()
        self.initialize_metadata()

    @abstractmethod
    def process(self, data: "Command"):
        raise NotImplementedError()

    def _compile_parameters(self, func_name: str, data: "Command") -> ParameterCompileResult:
        _results = {}
        _command = data._command
        # Raise a plugin error if the command name is missing from the command object. This should never happen.
        if _command is None:
            raise PluginError(f"Plugin '{self.plugin_name}' error: encountered an error compiling parameters due to a missing command value.")

        # Return a compile failure result if the command is disabled.
        if func_name in self.plugin_metadata.get(PluginCfgFields.PLUGIN.COMMANDS.DISABLE_COMMANDS, []):
            return ParameterCompileResult(
                status=PluginCompileConstants.Status.FAILED,
                reason=PluginCompileConstants.Reason.COMMAND_DISABLED,
            )
        # Return a compile failure result if the command is using more than 1 exclusive parameter at a time.
        if len(self.exclusive_parameters[_command]) > 0:
            params = [param.split("=")[0] for param in data.parameters]
            params = [param for param in params if param not in MessageRelayDefinitions.get_definitions()]
            if len(params) > 1:
                matching_parameters = [
                    param
                    for param in data.parameters
                    for param_exclusive in self.exclusive_parameters[_command]
                    if param.split("=")[0] == param_exclusive
                ]
                return ParameterCompileResult(
                    status=PluginCompileConstants.Status.FAILED,
                    reason=PluginCompileConstants.Reason.COMMAND_EXCLUSIVE,
                    parameters=[param.split("=")[0] for param in matching_parameters],
                )

        for param in data.parameters:
            param_split: List[str] = param.strip().split("=", 1)
            if len(param_split) == 0:
                param_split.append(param.strip())

            # If the parameter is a global plugin message relay parameter, execute the associated parameter function.
            if param_split[0] in MessageRelayDefinitions.get_definitions():
                continue

            # Return a compile failure result if the parameter is disabled for the specified command.
            if f"{_command}.{param_split[0]}" in self.plugin_metadata.get(PluginCfgFields.PLUGIN.COMMANDS.DISABLE_PARAMETERS, []):
                return ParameterCompileResult(
                    status=PluginCompileConstants.Status.FAILED,
                    reason=PluginCompileConstants.Reason.PARAMETER_DISABLED,
                    parameters=param_split[0],
                )
            # Return a compile failure if the parameter is invalid.
            elif param_split[0] not in self.command_parameters[_command]:
                return ParameterCompileResult(
                    status=PluginCompileConstants.Status.FAILED,
                    reason=PluginCompileConstants.Reason.PARAMETER_INVALID,
                    parameters=param_split[0],
                )

            # Execute the parameter function.
            func: Callable = getattr(self, f"_parameter_{func_name}_{param_split[0]}")
            _results[param_split[0]] = func(data, param)

        # Display all messages in the output queue.
        params = [param.split("=")[0] for param in data.parameters if param.split("=")[0] in MessageRelayDefinitions.get_definitions()]
        if not params:
            params = [MessageRelayDefinitions.ME]
        output = self.output_message_queue.dequeue()
        while output is not None:
            for param in params:
                func: Callable = getattr(plugin_output_parameters, f"output_{param}")
                func(*output)
            output = self.output_message_queue.dequeue()

        return ParameterCompileResult(
            status=PluginCompileConstants.Status.OK,
            result=_results,
        )

    def verify_parameters(self, func_name: str, data: "Command") -> Optional[Dict[str, Any]]:
        _compiled_result: ParameterCompileResult = self._compile_parameters(func_name, data)
        if _compiled_result.status == PluginCompileConstants.Status.FAILED:
            if _compiled_result.reason == PluginCompileConstants.Reason.COMMAND_DISABLED:
                GUIFramework.gui(
                    f"'{data.command}' command error: this command is disabled.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                )
                return
            elif _compiled_result.reason == PluginCompileConstants.Reason.COMMAND_EXCLUSIVE:
                if not _compiled_result.parameters:
                    _compiled_result.parameters = ["n/a"]
                GUIFramework.gui(
                    f"'{data.command}' command error: [{', '.join(_compiled_result.parameters)}] are exclusive "
                    "parameters that must be used independently.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                )
                return
            elif _compiled_result.reason == PluginCompileConstants.Reason.PARAMETER_DISABLED:
                GUIFramework.gui(
                    f"'{data.command}' command error: the '{_compiled_result.parameters}' parameter is disabled.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                )
                return
            elif _compiled_result.reason == PluginCompileConstants.Reason.PARAMETER_INVALID:
                GUIFramework.gui(
                    f"'{data.command}' command error: the '{_compiled_result.parameters}' parameter is invalid.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                )
                return
        _compiled_parameters: Optional[Dict[str, Any]] = _compiled_result.result
        if _compiled_parameters is None:
            GUIFramework.gui(
                f"'{data.command}' command error: parameters failed to compile.",
                target_users=mumble_utils.get_user_by_id(data.actor),
            )
            return
        return _compiled_parameters

    def initialize_metadata(self):
        self._plugin_metadata = Config(pathlib.Path.cwd() / f".config/plugins/{self._plugin_name}/metadata.toml")
        self._plugin_metadata.read()

    def initialize_parameters(self, callbacks: List[Dict[str, Any]]):
        if not callbacks:
            raise PluginError(f"Unable to initialize parameters for plugin '{self.plugin_name}'. No command callbacks provided.")
        for _clbk in callbacks:
            # Disable commands from plugin metadata file.
            if _clbk["command"] in self.plugin_metadata.get(PluginCfgFields.PLUGIN.COMMANDS.DISABLE_COMMANDS, []):
                logger.debug(
                    f"[{LogOutputIdentifiers.PLUGINS_PARAMETERS}]: Parameters for command '{_clbk['command']}' is disabled in the "
                    "plugin metadata file. Skipping parameter initialization..."
                )
                continue

            # Disable parameters from plugin metadata file.
            _enabled_parameters: List[str] = []
            _enabled_exclusive_parameters: List[str] = []
            _disabled_parameters: List[str] = self.plugin_metadata.get(PluginCfgFields.PLUGIN.COMMANDS.DISABLE_PARAMETERS, [])
            for parameter in _clbk["parameters"]:
                if f"{_clbk['command']}.{parameter}" in _disabled_parameters:
                    logger.debug(
                        f"[{LogOutputIdentifiers.PLUGINS_PARAMETERS}]: Parameter '{parameter}' for command '{_clbk['command']}' is disabled in the "
                        "plugin metadata file. Skipping parameter initialization..."
                    )
                    continue
                _enabled_parameters.append(parameter)
            for parameter in _clbk["exclusive_parameters"]:
                if parameter in _disabled_parameters:
                    logger.debug(
                        f"[{LogOutputIdentifiers.PLUGINS_PARAMETERS}]: Disabled exclusivity rules for command '{_clbk['command']}.{parameter}' as "
                        "the associated parameter is disabled."
                    )
                    continue
                _enabled_exclusive_parameters.append(parameter)

            self._command_parameters[_clbk["command"]] = _enabled_parameters
            self._exclusive_parameters[_clbk["command"]] = _enabled_exclusive_parameters
            logger.debug(
                f"[{LogOutputIdentifiers.PLUGINS_PARAMETERS}]: Plugin '{self.plugin_name}' parameters [{','.join(_enabled_parameters)}] for "
                f"command '{_clbk['command']}' initialized."
            )

    def start(self) -> Tuple[bool, str]:
        if not self._is_running:
            self._is_running = True
            self._thread_stop_event.clear()
            _msg = f"Plugin started: {self.plugin_name}"
            logger.debug(f"[{LogOutputIdentifiers.PLUGINS}]: {_msg}")
            return (True, _msg)
        _msg = f"Plugin '{self.plugin_name}' is already running."
        logger.debug(f"[{LogOutputIdentifiers.PLUGINS}]: {_msg}")
        return (False, _msg)

    def stop(self) -> Tuple[bool, str]:
        if self._is_running:
            self._thread_stop_event.set()
            self._is_running = False
            _msg = f"Plugin stopped: {self.plugin_name}"
            logger.debug(f"[{LogOutputIdentifiers.PLUGINS}]: {_msg}")
            return (True, _msg)
        _msg = f"Plugin '{self.plugin_name}' is already stopped."
        logger.warning(f"[{LogOutputIdentifiers.PLUGINS}]: {_msg}")
        return (False, _msg)

    def restart(self) -> Tuple[bool, str]:
        _plugin_stopped: Tuple[bool, str] = self.stop()
        _msg = ""
        if self.start():
            _msg = f"Plugin restarted: {self.plugin_name}"
            logger.debug(f"[{LogOutputIdentifiers.PLUGINS}]: {_msg}")
            return (True, _msg)
        if _plugin_stopped[0] is True:
            _msg = f"Plugin '{self.plugin_name}' was stopped during a restart process and could not be started again."
            logger.warning(f"[{LogOutputIdentifiers.PLUGINS}]: {_msg}")
        else:
            _msg = f"Plugin '{self.plugin_name}' could not be restarted."
            logger.error(f"[{LogOutputIdentifiers.PLUGINS}]: {_msg}")
        return (False, _msg)

    def quit(self):
        self.stop()
        logger.debug(f"[{LogOutputIdentifiers.PLUGINS}]: Plugin closed: {self.plugin_name}")
