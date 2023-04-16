import logging
import threading
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from ..constants import LogCfgFields, MumimoCfgFields
from ..exceptions import ServiceError
from ..lib.command_history import CommandHistory
from ..logging import log_privacy
from ..settings import settings
from ..utils import mumble_utils
from ..utils.parsers import cmd_parser

if TYPE_CHECKING:
    from pymumble_py3.mumble import Mumble

    from ..config import Config
    from ..lib.command import Command
    from ..log_config import LogConfig


logger = logging.getLogger(__name__)


class CommandProcessingService:
    class OutputPrivacyFilter:
        def get_privacy_template(self) -> Dict[str, Any]:
            return {
                "file": {
                    "message": None,
                    "command": None,
                    "actor": None,
                    "channel": None,
                    "parameters": None,
                },
                "console": {
                    "message": None,
                    "command": None,
                    "actor": None,
                    "channel": None,
                    "parameters": None,
                },
            }

        def compile_file_privacy_checked_message(self, redacted_output: Dict[str, Any]):
            return (
                f"Command Received::{redacted_output['file']['channel']}::{redacted_output['file']['actor']}::"
                f"[Cmd:{redacted_output['file']['command']} | Params:{redacted_output['file']['parameters']}]::"
                f"{redacted_output['file']['message']}"
            )

        def compile_console_privacy_checked_message(self, redacted_output: Dict[str, Any]):
            return (
                f"Command Received::{redacted_output['console']['channel']}::{redacted_output['console']['actor']}::"
                f"[Cmd:{redacted_output['console']['command']} | Params:{redacted_output['console']['parameters']}]::"
                f"{redacted_output['console']['message']}"
            )

        def _redact_commands(self, cmd: "Command", log_cfg: "LogConfig") -> Dict[str, Any]:
            _redacted_text = "Redacted"
            _dict = {"console": {}, "file": {}}
            if log_cfg.get(LogCfgFields.OUTPUT.CONSOLE.PRIVACY.REDACT_COMMANDS):
                _dict["console"]["command"] = _redacted_text
                _dict["console"]["parameters"] = _redacted_text
            else:
                _dict["console"]["command"] = cmd.command
                _dict["console"]["parameters"] = cmd.parameters
            if log_cfg.get(LogCfgFields.OUTPUT.FILE.PRIVACY.REDACT_COMMANDS):
                _dict["file"]["command"] = _redacted_text
                _dict["file"]["parameters"] = _redacted_text
            else:
                _dict["file"]["command"] = cmd.command
                _dict["file"]["parameters"] = cmd.parameters
            return _dict

        def _redact_actor(self, cmd: "Command", log_cfg: "LogConfig", connection_instance: "Mumble") -> Dict[str, Any]:
            _redacted_text = "Redacted"
            _dict = {"console": {}, "file": {}}
            _parsed_actor_name = cmd_parser.parse_actor_name(cmd, connection_instance)
            if log_cfg.get(LogCfgFields.OUTPUT.CONSOLE.PRIVACY.REDACT_USER):
                _dict["console"]["actor"] = _redacted_text
            else:
                _dict["console"]["actor"] = _parsed_actor_name
            if log_cfg.get(LogCfgFields.OUTPUT.FILE.PRIVACY.REDACT_USER):
                _dict["file"]["actor"] = _redacted_text
            else:
                _dict["file"]["actor"] = _parsed_actor_name
            return _dict

        def _redact_channel(self, cmd: "Command", log_cfg: "LogConfig", connection_instance: "Mumble") -> Dict[str, Any]:
            _redacted_text = "Redacted"
            _dict = {"console": {}, "file": {}}
            _parsed_channel_name = cmd_parser.parse_channel_name(cmd, connection_instance)
            if log_cfg.get(LogCfgFields.OUTPUT.CONSOLE.PRIVACY.REDACT_CHANNEL):
                _dict["console"]["channel"] = _redacted_text
            else:
                _dict["console"]["channel"] = _parsed_channel_name
            if log_cfg.get(LogCfgFields.OUTPUT.FILE.PRIVACY.REDACT_CHANNEL):
                _dict["file"]["channel"] = _redacted_text
            else:
                _dict["file"]["channel"] = _parsed_channel_name
            return _dict

        def _redact_message(self, cmd: "Command", log_cfg: "LogConfig") -> Dict[str, Any]:
            _redacted_message_text = "[Redacted Message]"
            _dict = {"console": {}, "file": {}}
            _parsed_message = cmd_parser.parse_message_image_data(cmd)
            _parsed_message = cmd_parser.parse_message_hyperlink_data(cmd)
            if log_cfg.get(LogCfgFields.OUTPUT.CONSOLE.PRIVACY.REDACT_MESSAGE):
                _dict["console"]["message"] = _redacted_message_text
            else:
                _dict["console"]["message"] = _parsed_message
            if log_cfg.get(LogCfgFields.OUTPUT.FILE.PRIVACY.REDACT_MESSAGE):
                _dict["file"]["message"] = _redacted_message_text
            else:
                _dict["file"]["message"] = _parsed_message
            return _dict

        def get_privacy_checked_output(
            self,
            cmd: "Command",
            log_cfg: "LogConfig",
            connection_instance: "Mumble",
        ):
            _dict = self.get_privacy_template()

            # Redact commands for file and console output:
            res = self._redact_commands(cmd, log_cfg)
            _dict["file"]["command"] = res["file"]["command"]
            _dict["console"]["command"] = res["console"]["command"]
            _dict["file"]["parameters"] = res["file"]["parameters"]
            _dict["console"]["parameters"] = res["console"]["parameters"]

            # Redact actor for file and console output:
            res = self._redact_actor(cmd, log_cfg, connection_instance)
            _dict["file"]["actor"] = res["file"]["actor"]
            _dict["console"]["actor"] = res["console"]["actor"]

            # Redact channel for file and console output:
            res = self._redact_channel(cmd, log_cfg, connection_instance)
            _dict["file"]["channel"] = res["file"]["channel"]
            _dict["console"]["channel"] = res["console"]["channel"]

            # Redact message for file and console output:
            res = self._redact_message(cmd, log_cfg)
            _dict["file"]["message"] = res["file"]["message"]
            _dict["console"]["message"] = res["console"]["message"]

            return _dict

    _connection_instance: "Mumble"
    _cmd_history: "CommandHistory"
    _privacy_filter: "OutputPrivacyFilter"
    _cfg_instance: "Config"
    _log_cfg: "LogConfig"

    @property
    def connection_instance(self) -> "Mumble":
        return self._connection_instance

    @property
    def cmd_history(self) -> "CommandHistory":
        return self._cmd_history

    @property
    def log_cfg(self) -> "LogConfig":
        return self._log_cfg

    def __init__(self, murmur_connection: "Mumble") -> None:
        self._connection_instance = murmur_connection
        if self.connection_instance is None:
            raise ServiceError("Unable to retrieve murmur connection: the murmur instance is not connected to a server.", logger=logger)
        _cfg_instance: Optional["Config"] = settings.configs.get_mumimo_config()
        if _cfg_instance is None:
            raise ServiceError("Unable to create command processing service: mumimo config could not be retrieved.", logger=logger)
        _log_cfg: Optional["LogConfig"] = settings.configs.get_log_config()
        if _log_cfg is None:
            raise ServiceError("Unable to create command processing service: log config could not be retrieved.", logger=logger)
        self._log_cfg = _log_cfg
        self._cmd_history = CommandHistory(history_limit=_cfg_instance.get(MumimoCfgFields.SETTINGS.COMMANDS.COMMAND_HISTORY_LENGTH, None))
        self._privacy_filter = self.OutputPrivacyFilter()

    def process_cmd(self, text) -> None:
        if text is None:
            raise ServiceError("Received text message with a 'None' value.", logger=logger)
        parsed_cmd: Optional["Command"] = cmd_parser.parse_command(text)
        if parsed_cmd is not None:
            # Exit command processing if the user message does not contain a command.
            _cmd_name = parsed_cmd.command
            if _cmd_name is None:
                return

            # Retrieve all the registered command callbacks to process the command.
            _callbacks = settings.commands.get_command_callbacks()
            if _callbacks is None:
                raise ServiceError("Unable to process command: cannot retrieve registered command callbacks.", logger=logger)

            # Retrieve the registered command information.
            _cmd_info: Optional[Dict[str, Any]] = _callbacks.get(_cmd_name)
            if _cmd_info is None:
                logger.warning(f"The command: [{_cmd_name}] is not a registered command.")
                return

            # Check if the plugin is currently active/running:
            _plugin_name: Optional[str] = _cmd_info.get("plugin", None)
            if _plugin_name is None:
                raise ServiceError(f"Unable to process command: registered command [{_cmd_name}] is missing a registered plugin name.", logger=logger)
            _registered_plugins = settings.plugins.get_registered_plugins()
            if _registered_plugins is None:
                raise ServiceError("Unable to process command: could not find any registered plugins.", logger=logger)
            if not _registered_plugins[_plugin_name].is_running:
                logger.warning(f"The command: [{_cmd_name}] could not be executed because the plugin is not running.")
                return

            # Retrieve the callable method for the command.
            _cmd_callable: Optional[Callable] = _cmd_info.get("func", None)
            if _cmd_callable is None:
                raise ServiceError(f"The command: [{_cmd_name}] does not contain a registered callable method.", logger=logger)

            # Ignore the command if the provided parameters are invalid:
            if parsed_cmd.parameters:
                _cmd_params: Optional[List[str]] = _cmd_info.get("parameters", [])
                if not any(param in _cmd_params for param in parsed_cmd.parameters):
                    logger.warning(f"The command: [{_cmd_name}] could not be executed because one or more provided parameters do not exist.")
                    mumble_utils.echo(
                        f"""Invalid command. Please use one of the available parameters: {'", "'.join(_cmd_params)}""",
                        target_type="me",
                        user_id=parsed_cmd.actor,
                    )
                    return

            # Handle the redaction of actor names, commands, messages, and channel names:
            if self.log_cfg is None:
                raise ServiceError("Unable to process command privacy checks: log config could not be retrieved.", logger=logger)
            _privacy_checked_output: Dict[str, Any] = self._privacy_filter.get_privacy_checked_output(
                parsed_cmd, self.log_cfg, self._connection_instance
            )

            # Add command to command history:
            if self.cmd_history is None:
                raise ServiceError("Unable to add command to uninitialized command history.", logger=logger)
            if self.cmd_history.add(parsed_cmd) is None:
                logger.warning(f"The command: [{parsed_cmd.message}] could not be added to the command history.")

            # Debug the command:
            log_privacy(
                msg=self._privacy_filter.compile_file_privacy_checked_message(_privacy_checked_output),
                logger=logger,
                level=logging.DEBUG,
            )

            # Execute the command's callable method in a new thread and pass in all command data.
            _cmd_thread = threading.Thread(
                name=f"mumimo-{_plugin_name}-{_cmd_name}",
                target=_cmd_callable,
                args=(_registered_plugins[_plugin_name], parsed_cmd),
            )
            logger.debug(f"Command thread: [{_cmd_thread.name}] initialized.")
            logger.debug(f"Command thread: [{_cmd_thread.name} | {_cmd_thread.ident}] starting...")
            _cmd_thread.start()

            logger.debug(f"Command thread: [{_cmd_thread.name} | {_cmd_thread.ident}] closing...")
            _cmd_thread.join()
            logger.debug(f"Command thread: [{_cmd_thread.name}] closed.")
