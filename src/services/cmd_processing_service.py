from typing import TYPE_CHECKING, Optional

from ..constants import MumimoCfgFields, LogCfgFields
from ..corelib.command_history import CommandHistory
from ..exceptions import ServiceError
from ..logging import debug as _debug
from ..logging import get_logger
from ..logging import print as _print
from ..logging import print_warning
from ..settings import settings
from ..utils.parsers import cmd_parser

if TYPE_CHECKING:
    from pymumble_py3.mumble import Mumble

    from ..log_config import LogConfig
    from ..corelib.command import Command


_logger = get_logger(__name__)
print = _print(_logger)
debug = _debug(logger=_logger)
warning = print_warning(logger=_logger)


class CommandProcessingService:
    _log_cfg: "LogConfig"
    _connection_instance: "Mumble"
    _cmd_history: "CommandHistory"

    @property
    def connection_instance(self) -> "Mumble":
        return self._connection_instance

    @property
    def cmd_history(self) -> "CommandHistory":
        return self._cmd_history

    def __init__(self, murmur_connection: "Mumble") -> None:
        self._connection_instance = murmur_connection
        if self.connection_instance is None:
            raise ServiceError("Unable to retrieve murmur connection: the murmur instance is not connected to a server.", logger=_logger)
        _cfg_instance = settings.get_mumimo_config()
        if _cfg_instance is None:
            raise ServiceError("Unable to create command processing service: mumimo config could not be retrieved.", logger=_logger)
        self._cfg_instance = _cfg_instance
        _log_cfg = settings.get_log_config()
        if _log_cfg is None:
            raise ServiceError("Unable to create command processing service: log config could not be retrieved.", logger=_logger)
        self._log_cfg = _log_cfg
        self._cmd_history = CommandHistory(history_limit=self._cfg_instance.get(MumimoCfgFields.SETTINGS.COMMANDS.COMMAND_HISTORY_LENGTH, None))

    def process_cmd(self, text) -> None:
        if text is None:
            raise ServiceError("Received text message with a 'None' value.", logger=_logger)
        parsed_cmd: Optional["Command"] = cmd_parser.parse_command(text)
        if parsed_cmd is not None:
            actor_name: str = cmd_parser.parse_actor_name(parsed_cmd, self.connection_instance)
            channel_name: str = cmd_parser.parse_channel_name(parsed_cmd, self.connection_instance)

            if self._log_cfg.get(LogCfgFields.OUTPUT.FILE.MESSAGE_PRIVACY):
                actor_name = "Redacted"
                channel_name = "Redacted"
                parsed_cmd.message = "[Redacted Message]"
            else:
                parsed_cmd.message = cmd_parser.parse_message_image_data(parsed_cmd)
                parsed_cmd.message = cmd_parser.parse_message_hyperlink_data(parsed_cmd)

            # Add command to command history:
            if self.cmd_history is None:
                raise ServiceError("Unable to add command to uninitialized command history.", logger=_logger)
            if self.cmd_history.add(parsed_cmd) is None:
                warning(f"The command: [{parsed_cmd.message}] could not be added to the command history.")

            debug(f"{channel_name}::{actor_name}::[Cmd:{parsed_cmd.command} | Params:{parsed_cmd.parameters}]::{parsed_cmd.message}")
