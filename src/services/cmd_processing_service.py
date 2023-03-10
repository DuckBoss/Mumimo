from typing import TYPE_CHECKING, Optional

from ..constants import MumimoCfgFields
from ..corelib.command_history import CommandHistory
from ..exceptions import ServiceError
from ..logging import debug as _debug
from ..logging import get_logger
from ..logging import print as _print
from ..logging import print_warning
from ..utils import config_utils
from ..utils.parsers import cmd_parser

if TYPE_CHECKING:
    from pymumble_py3.mumble import Mumble

    from ..config import Config
    from ..corelib.command import Command


_logger = get_logger(__name__)
print = _print(_logger)
debug = _debug(logger=_logger)
warning = print_warning(logger=_logger)


class CommandProcessingService:
    _cfg_instance: "Config"
    _connection_instance: "Mumble"
    _cmd_history: "CommandHistory"

    @property
    def connection_instance(self) -> "Mumble":
        return self._connection_instance

    @property
    def cfg_instance(self) -> "Config":
        return self._cfg_instance

    @property
    def cmd_history(self) -> "CommandHistory":
        return self._cmd_history

    def __init__(self, murmur_connection: "Mumble", cfg_instance: Optional["Config"] = None) -> None:
        self._connection_instance = murmur_connection
        if self.connection_instance is None:
            raise ServiceError("Unable to retrieve murmur connection: the murmur instance is not connected to a server.", logger=_logger)
        if cfg_instance is not None:
            self._cfg_instance = cfg_instance
        else:
            self._cfg_instance = config_utils.get_config_instance()
            if self.cfg_instance is None:
                raise ServiceError("Unable to create command processing service: config instance could not be retrieved.", logger=_logger)
        self._cmd_history = CommandHistory(history_limit=self.cfg_instance.get(MumimoCfgFields.SETTINGS.COMMANDS.COMMAND_HISTORY_LENGTH, None))

    def process_cmd(self, text) -> None:
        if text is None:
            raise ServiceError("Received text message with a 'None' value.", logger=_logger)
        parsed_cmd: Optional["Command"] = cmd_parser.parse_command(text, self.cfg_instance)
        if parsed_cmd is not None:
            actor_name: str = cmd_parser.parse_actor_name(parsed_cmd, self.connection_instance)
            channel_name: str = cmd_parser.parse_channel_name(parsed_cmd, self.connection_instance)
            parsed_cmd.message = cmd_parser.parse_message_image_data(parsed_cmd)
            parsed_cmd.message = cmd_parser.parse_message_hyperlink_data(parsed_cmd)

            # Add command to command history:
            if self.cmd_history is None:
                raise ServiceError("Unable to add command to uninitialized command history.", logger=_logger)
            if self.cmd_history.add(parsed_cmd) is None:
                warning(f"The command: [{parsed_cmd.message}] could not be added to the command history.")

            debug(f"{channel_name}::{actor_name}::[Cmd:{parsed_cmd.command} | Params:{parsed_cmd.parameters}]::{parsed_cmd.message}")
