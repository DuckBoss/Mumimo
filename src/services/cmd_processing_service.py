import logging
import threading
import asyncio
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional


from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..lib.database.models.user import UserTable
from ..lib.database.models.permission_group import PermissionGroupTable
from ..lib.database.models.command import CommandTable
from ..lib.database.models.alias import AliasTable

from ..constants import LogCfgFields, MumimoCfgFields, LogOutputIdentifiers
from ..exceptions import ServiceError
from ..lib.command_history import CommandHistory
from ..logging import log_privacy
from ..settings import settings
from ..utils import mumble_utils
from ..utils.parsers import cmd_parser
from ..lib.command_queue import CommandQueue

if TYPE_CHECKING:
    from pymumble_py3.mumble import Mumble
    from pymumble_py3.users import User

    from ..config import Config
    from ..lib.command import Command
    from ..log_config import LogConfig

    from ..services.database_service import DatabaseService


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
    _privacy_filter: "OutputPrivacyFilter"
    _cfg_instance: "Config"
    _log_cfg: "LogConfig"
    _cmd_queue: "CommandQueue"

    @property
    def connection_instance(self) -> "Mumble":
        return self._connection_instance

    @property
    def log_cfg(self) -> "LogConfig":
        return self._log_cfg

    @property
    def command_queue(self) -> "CommandQueue":
        return self._cmd_queue

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
        settings.commands.history.set_command_history(
            CommandHistory(history_limit=_cfg_instance.get(MumimoCfgFields.SETTINGS.COMMANDS.COMMAND_HISTORY_LENGTH, None))
        )
        self._privacy_filter = self.OutputPrivacyFilter()
        self._cmd_queue = CommandQueue(max_size=_cfg_instance.get(MumimoCfgFields.SETTINGS.COMMANDS.COMMAND_HISTORY_LENGTH, None))

    def process_cmd(self, text) -> None:
        if text is None:
            raise ServiceError("Received text message with a 'None' value.", logger=logger)

        asyncio.run(self._process_alias(text))
        asyncio.run(self._process_cmd())

    async def _process_alias(self, text) -> None:
        parsed_cmd: Optional["Command"] = cmd_parser.parse_command(text)
        if parsed_cmd is not None:
            # Exit command processing if the user message does not contain a command.
            _cmd_name = parsed_cmd.command
            if _cmd_name is None:
                return

            # Retrieve the database service.
            _db_service: Optional["DatabaseService"] = settings.database.get_database_instance()
            if not _db_service:
                raise ServiceError("Unable to process command: the database service could not retrieve the database instance.", logger=logger)

            async with _db_service.session() as session:
                # Check if the command is an alias.
                _alias_query = await session.execute(select(AliasTable).filter_by(name=_cmd_name).options(selectinload(AliasTable.permission_groups)))
                _alias_info: Optional[AliasTable] = _alias_query.scalar()
                if not _alias_info:
                    logger.debug(f"No aliases found for '{_cmd_name}' in the database. Continuing to process as command...")
                    if self.command_queue.enqueue(parsed_cmd):
                        logger.debug(f"Enqueued command: '{parsed_cmd.command}'.")
                        return
                    logger.error(f"Encountered an error enqueueing command: '{parsed_cmd.command}'")
                    return

                # Process a generic alias:
                if _alias_info.is_generic:
                    logger.debug(f"Detected generic alias '{_cmd_name}'. Processing generic commands...")
                    _generic_messages: List[str] = _alias_info.command.split("|")
                    for _message in _generic_messages:
                        logger.debug(f"Processing generic command: '{_message}'")
                        _new_text_object = deepcopy(text)
                        _new_text_object.message = _message
                        _new_parsed_cmd: Optional["Command"] = cmd_parser.parse_command(_new_text_object)
                        if not _new_parsed_cmd:
                            logger.warning(f"Generic command not recognized: '{_message}'. Skipping command...")
                            continue
                        self.command_queue.enqueue(_new_parsed_cmd)
                    await self._process_cmd()
                    return
                # Process a non-generic alias:
                _alias_cmd_query = await session.execute(select(CommandTable).filter_by(name=_alias_info.command))
                _alias_cmd_info: Optional[CommandTable] = _alias_cmd_query.scalar()
                if not _alias_cmd_info:
                    logger.warning(
                        f"[{LogOutputIdentifiers.DB_ALIASES}]: Unable to execute non-generic alias '{_alias_info.name}': the command for this "
                        "alias does not exist in the database."
                    )
                    return
                parsed_cmd.command = _alias_cmd_info.name
                if self.command_queue.enqueue(parsed_cmd):
                    logger.debug(f"Detected non-generic alias '{_cmd_name}'. Enqueued command: '{parsed_cmd.command}'.")
                    return
                logger.error(f"Encountered an error enqueueing command: '{parsed_cmd.command}'")

    async def _process_cmd(self) -> None:
        for _ in range(self.command_queue.size):
            # Retrieve the command from the queue if the queue is not empty.
            command = self.command_queue.dequeue()
            if command is None:
                return
            logger.debug(f"Processing command: '{command.command}'...")

            # Retrieve the command name.
            _cmd_name = command.command
            if _cmd_name is None:
                return

            # Retrieve all the registered command callbacks to process the command.
            _callbacks = settings.commands.callbacks.get_command_callbacks()
            if _callbacks is None:
                raise ServiceError("Unable to process command: cannot retrieve registered command callbacks.", logger=logger)

            # Retrieve the registered command information.
            _cmd_info: Optional[Dict[str, Any]] = _callbacks.get(_cmd_name)
            if _cmd_info is None:
                logger.warning(f"The command: [{_cmd_name}] is not a registered command.")
                return

            # Retrieve the user's and command's permission groups to determine if the user can use this commnad.
            _db_service: Optional["DatabaseService"] = settings.database.get_database_instance()
            if not _db_service:
                raise ServiceError("Unable to process command: the database service could not retrieve the database instance.", logger=logger)

            _actor_name: Optional["User"] = mumble_utils.get_user_by_id(command.actor)
            if not _actor_name:
                raise ServiceError("Unable to process command: the user name could not be retrieved from the actor id.")

            async with _db_service.session() as session:
                _user_query = await session.execute(
                    select(UserTable).filter_by(name=_actor_name["name"]).options(selectinload(UserTable.permission_groups))
                )
                _user_info: Optional[UserTable] = _user_query.scalar()
                if not _user_info:
                    logger.error("Unable to process command: the user that sent this command was not found in the database.")
                    return

                _command_query = await session.execute(
                    select(CommandTable).filter_by(name=_cmd_name).options(selectinload(CommandTable.permission_groups))
                )
                _command_info: Optional[CommandTable] = _command_query.scalar()
                if not _command_info:
                    logger.error("Unable to process command: the command was not found in the database.")
                    return

                _user_permissions_groups: List[PermissionGroupTable] = _user_info.permission_groups
                _command_permission_groups: List[PermissionGroupTable] = _command_info.permission_groups
                _user_permissions_list = [perm.to_dict() for perm in _user_permissions_groups]

                _command_permissions_list = [perm.to_dict() for perm in _command_permission_groups]
                _command_permissions_list = [cmd_perm["name"] for cmd_perm in _command_permissions_list]
                permission_found: bool = False
                for _user_permission in _user_permissions_list:
                    if _user_permission["name"] in _command_permissions_list:
                        permission_found = True
                        break
                if not permission_found:
                    mumble_utils.echo(
                        f"Unable to process command: the user '{_user_info.name}' does not have permissions to use the '{_cmd_name}' command.",
                        target_users=mumble_utils.get_user_by_id(command.actor),
                        log_severity=logging.WARNING,
                    )
                    return

            # Check if the plugin is currently active/running:
            _plugin_name: Optional[str] = _cmd_info.get("plugin", None)
            if _plugin_name is None:
                raise ServiceError(f"Unable to process command: registered command [{_cmd_name}] is missing a registered plugin name.", logger=logger)
            _registered_plugins = settings.plugins.get_registered_plugins()
            if _registered_plugins is None:
                raise ServiceError("Unable to process command: could not find any registered plugins.", logger=logger)
            if not _registered_plugins[_plugin_name].is_running:
                _inactive_msg = f"The command '{_cmd_name}' could not be executed because the plugin '{_plugin_name}' is not running."
                logger.warning(_inactive_msg)
                mumble_utils.echo(
                    _inactive_msg,
                    target_users=mumble_utils.get_user_by_id(command.actor),
                )
                return

            # Retrieve the callable method for the command.
            _cmd_callable: Optional[Callable] = _cmd_info.get("func", None)
            if _cmd_callable is None:
                raise ServiceError(f"The command: [{_cmd_name}] does not contain a registered callable method.", logger=logger)

            # Ignore the command if the provided parameters are invalid or do not exist:
            _cmd_params: Optional[List[str]] = _cmd_info.get("parameters", [])
            if len(_cmd_params) > 0:
                _parameters_required = _cmd_info.get("parameters_required", False)
                if _parameters_required and not command.parameters:
                    logger.warning(f"The command: [{_cmd_name}] requires parameters and no parameters were provided.")
                    mumble_utils.echo(
                        f"Invalid '{_cmd_name}' command. This command requires the usage of parameters. "
                        f"Please use one of the available parameters: {', '.join(_cmd_params)}",
                        target_users=mumble_utils.get_user_by_id(command.actor),
                    )
                    return
                if any(param.split("=", 1)[0] not in _cmd_params for param in command.parameters):
                    logger.warning(f"The command: [{_cmd_name}] could not be executed because one or more provided parameters do not exist.")
                    mumble_utils.echo(
                        f"Invalid '{_cmd_name}' command. Please use one of the available parameters: {', '.join(_cmd_params)}",
                        target_users=mumble_utils.get_user_by_id(command.actor),
                        user_id=command.actor,
                    )
                    return

            # Handle the redaction of actor names, commands, messages, and channel names:
            if self.log_cfg is None:
                raise ServiceError("Unable to process command privacy checks: log config could not be retrieved.", logger=logger)
            _privacy_checked_output: Dict[str, Any] = self._privacy_filter.get_privacy_checked_output(
                command, self.log_cfg, self._connection_instance
            )

            # Add command to command history:
            if settings.commands.history.get_command_history() is None:
                raise ServiceError("Unable to add command to uninitialized command history.", logger=logger)
            if settings.commands.history.add_command_to_history(command) is None:
                logger.warning(f"The command: [{command.message}] could not be added to the command history.")

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
                args=(_registered_plugins[_plugin_name], command),
            )
            logger.debug(f"Command thread: [{_cmd_thread.name}] initialized.")
            _cmd_thread.start()
            logger.debug(f"Command thread: [{_cmd_thread.name} | {_cmd_thread.ident}] starting...")

            logger.debug(f"Command thread: [{_cmd_thread.name} | {_cmd_thread.ident}] completing...")
            _cmd_thread.join()
            logger.debug(f"Command thread: [{_cmd_thread.name}] closed.")
