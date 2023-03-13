from typing import TYPE_CHECKING, Optional, Dict, Any

from ..constants import MumimoCfgFields, LogCfgFields
from ..corelib.command_history import CommandHistory
from ..exceptions import ServiceError
from ..logging import debug as _debug
from ..logging import get_logger
from ..logging import print as _print
from ..logging import print_warning
from ..settings import settings
from ..utils.parsers import cmd_parser
from ..utils.log_utils import privacy_file_redact_all_check, privacy_console_redact_all_check

if TYPE_CHECKING:
    from pymumble_py3.mumble import Mumble
    from ..log_config import LogConfig
    from ..corelib.command import Command


_logger = get_logger(__name__)
print = _print(_logger)
debug = _debug(logger=_logger)
warning = print_warning(logger=_logger)


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
                f"{redacted_output['file']['channel']}::{redacted_output['file']['actor']}::"
                f"[Cmd:{redacted_output['file']['command']} | Params:{redacted_output['file']['parameters']}]::"
                f"{redacted_output['file']['message']}"
            )

        def compile_console_privacy_checked_message(self, redacted_output: Dict[str, Any]):
            return (
                f"{redacted_output['console']['channel']}::{redacted_output['console']['actor']}::"
                f"[Cmd:{redacted_output['console']['command']} | Params:{redacted_output['console']['parameters']}]::"
                f"{redacted_output['console']['message']}"
            )

        def get_privacy_checked_output(
            self,
            cmd: "Command",
            log_cfg: "LogConfig",
            connection_instance: "Mumble",
        ):
            _dict = self.get_privacy_template()
            _redacted_text = "Redacted"
            _redacted_message_text = "[Redacted Message]"

            # Redact commands for file and console output:
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

            # Redact actor for file and console output:
            _parsed_actor_name = cmd_parser.parse_actor_name(cmd, connection_instance)
            if log_cfg.get(LogCfgFields.OUTPUT.CONSOLE.PRIVACY.REDACT_USER):
                _dict["console"]["actor"] = _redacted_text
            else:
                _dict["console"]["actor"] = _parsed_actor_name
            if log_cfg.get(LogCfgFields.OUTPUT.FILE.PRIVACY.REDACT_USER):
                _dict["file"]["actor"] = _redacted_text
            else:
                _dict["file"]["actor"] = _parsed_actor_name

            # Redact channel for file and console output:
            _parsed_channel_name = cmd_parser.parse_channel_name(cmd, connection_instance)
            if log_cfg.get(LogCfgFields.OUTPUT.CONSOLE.PRIVACY.REDACT_CHANNEL):
                _dict["console"]["channel"] = _redacted_text
            else:
                _dict["console"]["channel"] = _parsed_channel_name
            if log_cfg.get(LogCfgFields.OUTPUT.FILE.PRIVACY.REDACT_CHANNEL):
                _dict["file"]["channel"] = _redacted_text
            else:
                _dict["file"]["channel"] = _parsed_channel_name

            # Redact message for file and console output:
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

    _log_cfg: "LogConfig"
    _connection_instance: "Mumble"
    _cmd_history: "CommandHistory"
    _privacy_filter: "OutputPrivacyFilter"

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
        self._privacy_filter = self.OutputPrivacyFilter()

    def process_cmd(self, text) -> None:
        if text is None:
            raise ServiceError("Received text message with a 'None' value.", logger=_logger)
        parsed_cmd: Optional["Command"] = cmd_parser.parse_command(text)
        if parsed_cmd is not None:

            # Handle the redaction of actor names, commands, messages, and channel names:
            _privacy_checked_output: Dict[str, Any] = self._privacy_filter.get_privacy_checked_output(
                parsed_cmd, self._log_cfg, self._connection_instance
            )

            # Add command to command history:
            if self.cmd_history is None:
                raise ServiceError("Unable to add command to uninitialized command history.", logger=_logger)
            if self.cmd_history.add(parsed_cmd) is None:
                warning(f"The command: [{parsed_cmd.message}] could not be added to the command history.")

            # Debug the processed command to the log file.
            debug(
                msg=self._privacy_filter.compile_file_privacy_checked_message(_privacy_checked_output),
                skip_file=privacy_file_redact_all_check(),
                skip_console=True,
            )
            # Debug the processed command to the console.
            debug(
                msg=self._privacy_filter.compile_console_privacy_checked_message(_privacy_checked_output),
                skip_file=True,
                skip_console=privacy_console_redact_all_check(),
            )
