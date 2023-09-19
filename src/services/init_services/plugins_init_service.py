import logging
import pathlib
import shutil
import sys
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import select

from ...config import Config
from ...constants import LogOutputIdentifiers, MumimoCfgFields, PluginCfgFields
from ...exceptions import ServiceError
from ...lib.command_callbacks import CommandCallbacks
from ...lib.database.models.command import CommandTable
from ...lib.database.models.permission_group import PermissionGroupTable
from ...lib.database.models.plugin import PluginTable
from ...settings import settings

if TYPE_CHECKING:
    from ...services.database_service import DatabaseService


logger = logging.getLogger(__name__)


class PluginsInitService:
    _sys_args: Dict[str, str] = {}

    def __init__(self, sys_args: Dict[str, str]) -> None:
        self._sys_args = sys_args

    async def initialize_plugins(self, db_service: "DatabaseService"):
        # Ensure the config and client state are both initialized.
        _cfg = settings.configs.get_mumimo_config()
        if _cfg is None:
            raise ServiceError("Unable to initialize plugins: the mumimo config is uninitialized.", logger=logger)
        # Ensure the plugin path exists.
        _plugin_path: pathlib.Path = pathlib.Path.cwd() / _cfg.get(MumimoCfgFields.SETTINGS.PLUGINS.PLUGINS_PATH)
        if not _plugin_path.exists() or not _plugin_path.is_dir():
            raise ServiceError(
                f"Unable to initialize plugins: the plugins path is invalid. Please check your config settings: '{_plugin_path}'", logger=logger
            )

        # Retrieve all the plugin directories in the root plugin folder.
        _plugin_dirs: List[pathlib.Path] = []
        for dir in _plugin_path.iterdir():
            if dir.is_dir() and dir.name != "__pycache__":
                _plugin_dirs.append(dir)

        # Iterate over each plugin directory and ensure each plugin has a metadata file.
        # Skip any directories that do not have a metadata file.

        _skipped_plugins = []
        for dir in _plugin_dirs:
            _plugin_name = dir.name

            # Skip the plugin if it is disabled in the mumimo config file.
            if _plugin_name in _cfg.get(MumimoCfgFields.SETTINGS.PLUGINS.DISABLED_PLUGINS, []):
                logger.info(
                    f"[{LogOutputIdentifiers.PLUGINS}]: Plugin '{_plugin_name}' is disabled in the mumimo config file. "
                    "Skipping plugin initialization..."
                )
                _skipped_plugins.append(_plugin_name)
                continue

            if not (dir / "plugin.py").is_file():
                logger.error(
                    f"[{LogOutputIdentifiers.PLUGINS}]: Plugin '{_plugin_name}' does not contain a 'plugin.py' file. "
                    "Skipping plugin initialization..."
                )
                _skipped_plugins.append(_plugin_name)
                continue

            _plugin_config_path: pathlib.Path = pathlib.Path.cwd() / _cfg.get(MumimoCfgFields.SETTINGS.PLUGINS.PLUGINS_CONFIG_PATH) / _plugin_name
            try:
                # Create the plugin's config directory if it does not exist and create the 'metadata.toml' from the template file.
                if not pathlib.Path.is_dir(_plugin_config_path):
                    pathlib.Path.mkdir(_plugin_config_path, parents=True, exist_ok=True)
                    logger.warning(
                        f"[{LogOutputIdentifiers.PLUGINS}]: Config directory not found for '{_plugin_name}' plugin. "
                        "Generating config directory now..."
                    )
                    if not (dir / "metadata_template.toml").is_file():
                        logger.error(
                            f"[{LogOutputIdentifiers.PLUGINS}]: Plugin '{_plugin_name}' does not contain a 'metadata_template.toml' file. "
                            "Skipping plugin initialization..."
                        )
                        _skipped_plugins.append(_plugin_name)
                        continue
                    shutil.copy(dir / "metadata_template.toml", _plugin_config_path / "metadata.toml")
                # If the plugin config directory already exists but the 'metadata.toml' file is missing, then skip plugin initialization.
                elif not (_plugin_config_path / "metadata.toml").is_file():
                    logger.warning(
                        f"[{LogOutputIdentifiers.PLUGINS}]: '{_plugin_name}' plugin does not contain a 'metadata.toml' file. "
                        "Skipping plugin initialization..."
                    )
                    continue
            except IOError as exc:
                raise ServiceError(f"Unable to create config directory for '{_plugin_name}' plugin.", logger=logger) from exc

            # Attempt to load in plugin metadata. Skip the plugin initialization if this step fails.
            _plugin_cfg = Config(_plugin_config_path / "metadata.toml")
            _plugin_cfg.read()
            if not _plugin_cfg:
                logger.error(
                    f"[{LogOutputIdentifiers.PLUGINS}]: Plugin '{_plugin_name}' encountered an error while processing the metadata file. "
                    "Skipping plugin initialization..."
                )
                _skipped_plugins.append(_plugin_name)
                continue
            # Skip the plugin initialization if the plugin is not enabled in the plugin metadata file.
            if not _plugin_cfg.get(PluginCfgFields.PLUGIN.ENABLED, False):
                logger.info(
                    f"[{LogOutputIdentifiers.PLUGINS}]: Plugin '{_plugin_name}' is not enabled in the plugin 'metadata.toml' file. "
                    "Skipping plugin initialization..."
                )
                _skipped_plugins.append(_plugin_name)
                continue

            sys.path.insert(0, str(_plugin_path.resolve()))
            _registered_plugin = __import__(f"{_plugin_name}.plugin", fromlist=["*"]).Plugin
            sys.path.pop(0)

            _plugin_commands: CommandCallbacks = CommandCallbacks()
            # Register all the commands belonging to this plugin.
            try:
                for command_name, command_value in _registered_plugin.command.all.items():
                    _plugin_commands.register_command(
                        callback_name=command_name,
                        plugin_name=_plugin_name,
                        command_func=command_value[0],
                        command_parameters=command_value[1],
                        parameters_required=command_value[2],
                        exclusive_parameters=command_value[3],
                        global_parameters=command_value[4],
                    )
                    logger.debug(
                        f"[{LogOutputIdentifiers.PLUGINS_COMMANDS}]: Registered '{_plugin_name}.{command_name}.[{'|'.join(command_value[1])}]' "
                        "plugin command."
                    )
                settings.commands.callbacks.add_command_callbacks(_plugin_commands)
            except AttributeError as exc:
                raise ServiceError(
                    f"Unable to initialize '{_plugin_name}' plugin. The command attribute does not exist in the plugin class.", logger=logger
                ) from exc

            # Import the plugin to the database and associate it with the plugin commands.
            _abort_import: bool = False
            async with db_service.session() as session:
                _query = await session.execute(select(PluginTable).filter_by(name=_plugin_name))
                _db_plugin: Optional[PluginTable] = _query.scalar()
                _plugin_modified: bool = False
                if _db_plugin is not None:
                    logger.debug(f"[{LogOutputIdentifiers.DB_PLUGINS}]: Plugin '{_plugin_name}' already exists in the database. Skipping import...")
                else:
                    _db_plugin = PluginTable(name=_plugin_name)
                    _plugin_modified = True
                    logger.debug(
                        f"[{LogOutputIdentifiers.DB_PLUGINS}]: Plugin '{_plugin_name}' not detected in the database. This plugin will be imported."
                    )
                # Import plugin commands to the database with plugin-specified default permissions if the command does not already exist.
                _imported_cmd_count: int = 0
                _cfg_disabled_commands: List[str] = _plugin_cfg.get(PluginCfgFields.PLUGIN.COMMANDS.DISABLE_COMMANDS, [])
                for command_name, command_value in _plugin_commands.items():
                    if command_name in _cfg_disabled_commands:
                        logger.debug(
                            f"[{LogOutputIdentifiers.PLUGINS_COMMANDS}]: Command '{command_name}' is disabled in the "
                            "plugin '{_plugin_name}' metadata file. Skipping import..."
                        )
                        continue

                    _query = await session.execute(select(CommandTable).filter_by(name=command_name))
                    _command: Optional[CommandTable] = _query.scalar()
                    if _command is not None:
                        logger.debug(
                            f"[{LogOutputIdentifiers.DB_PLUGINS_COMMANDS}]: Command '{command_name}' already exists in the database. "
                            "Skipping import..."
                        )
                        continue

                    _cfg_plugin_cmd_permission_names: List[str] = _plugin_cfg.get(PluginCfgFields.PLUGIN.COMMANDS.DEFAULT_PERMISSION_GROUPS, [])

                    _new_command = CommandTable(name=command_name)

                    for _permission_name in _cfg_plugin_cmd_permission_names:
                        _query = await session.execute(select(PermissionGroupTable).filter_by(name=_permission_name))
                        _permission: Optional[PermissionGroupTable] = _query.scalar()
                        if not _permission:
                            logger.error(
                                f"[{LogOutputIdentifiers.PLUGINS_PERMISSIONS}]: Default permission group '{_permission_name}' from the "
                                f"plugin '{_plugin_name}' does not exist in the database. Aborting plugin initialization..."
                            )
                            _skipped_plugins.append(_plugin_name)
                            _abort_import = True
                            break
                        _new_command.permission_groups.append(_permission)
                        logger.debug(
                            f"[{LogOutputIdentifiers.PLUGINS_PERMISSIONS}]: Added permission group '{_permission_name}' to '{command_name}' command."
                        )
                    if _abort_import:
                        break

                    _db_plugin.commands.append(_new_command)
                    _imported_cmd_count += 1
                    _plugin_modified = True

                    logger.debug(
                        f"[{LogOutputIdentifiers.DB_PLUGINS_COMMANDS}]: Command '{command_name}' not detected in the database. "
                        "This command will be imported."
                    )

                # Abort the plugin import process and revert registering command callbacks if there was an error during database initialization.
                if _abort_import:
                    logger.debug(
                        f"[{LogOutputIdentifiers.DB_PLUGINS_COMMANDS}]: Aborting plugin commands database import process "
                        f"for '{_plugin_name}' plugin: rolling back database modifications and unregistering plugin commands."
                    )
                    await session.rollback()
                    _unregister_status, _unregisters = _plugin_commands.unregister_plugin(_plugin_name)
                    if not _unregister_status:
                        _failed: List[Dict[str, Any]] = [dict_val for dict_key, dict_val in _unregisters.items()]
                        logger.error(
                            f"[{LogOutputIdentifiers.DB_PLUGINS_COMMANDS}]: Encountered an error unregistering plugin '{_plugin_name}' during "
                            f"abort process. The following commands failed to unregister: [{', '.join([item['command'] for item in _failed])}]"
                        )
                    else:
                        _success: List[Dict[str, Any]] = [dict_val for dict_key, dict_val in _unregisters.items()]
                        logger.debug(
                            f"[{LogOutputIdentifiers.DB_PLUGINS_COMMANDS}]: Rolling back plugin '{_plugin_name}' command registrations. "
                            f"The following commands have been unregistered: [{', '.join([item['command'] for item in _success])}]"
                        )
                    settings.commands.callbacks.set_command_callbacks(_plugin_commands)
                    continue

                # Add the plugin and associated commands to the database if any modifications were detected since the previous run.
                if _plugin_modified:
                    session.add(_db_plugin)
                    await session.commit()
                    logger.debug(
                        f"[{LogOutputIdentifiers.DB_PLUGINS}]: Imported plugin '{_plugin_name}' in the database "
                        f"with {_imported_cmd_count} new commands."
                    )
                else:
                    logger.debug(
                        f"[{LogOutputIdentifiers.DB_PLUGINS}]: Plugin '{_plugin_name}' already exists in the database and was "
                        "unmodified from the previous run. No new database imports conducted."
                    )
                    await session.rollback()

            if not _abort_import:
                _plugin = _registered_plugin(_plugin_name)
                _plugin.start()
                settings.plugins.set_registered_plugin(_plugin_name, _plugin)

        logger.info(
            f"[{LogOutputIdentifiers.PLUGINS}]: Initialized plugins: [{', '.join([k for k, v in settings.plugins.get_registered_plugins().items()])}]"
        )
        if _skipped_plugins:
            logger.warning(f"[{LogOutputIdentifiers.PLUGINS}]: The following plugins were not initialized: [{', '.join(_skipped_plugins)}]")
