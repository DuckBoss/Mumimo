import logging
import pathlib
import shutil
import sys
from typing import TYPE_CHECKING, Dict, List, Optional

from sqlalchemy import select

from ...config import Config
from ...constants import MumimoCfgFields, PluginCfgFields
from ...exceptions import ServiceError
from ...lib.command_callbacks import CommandCallbacks
from ...lib.database.models.command import CommandTable
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
        _cfg = settings.get_mumimo_config()
        if _cfg is None:
            raise ServiceError("Unable to initialize plugins: the mumimo config is uninitialized.", logger=logger)
        # Ensure the plugin path exists.
        _plugin_path: pathlib.Path = pathlib.Path.cwd() / _cfg.get(MumimoCfgFields.SETTINGS.PLUGINS.PLUGINS_PATH)
        if not _plugin_path.exists() or not _plugin_path.is_dir():
            raise ServiceError(
                f"Unable to initialize plugins: the plugins path is invalid. Please check your config settings: '{_plugin_path}'", logger=logger
            )

        _registered_plugins = settings.get_registered_plugins()
        # Retrieve all the plugin directories in the root plugin folder.
        _plugin_dirs: List[pathlib.Path] = []
        for dir in _plugin_path.iterdir():
            if dir.is_dir() and dir.name != "__pycache__":
                _plugin_dirs.append(dir)

        # Iterate over each plugin directory and ensure each plugin has a metadata file.
        # Skip any directories that do not have a metadata file.
        sys.path.insert(0, str(_plugin_path.resolve()))
        for dir in _plugin_dirs:
            _plugin_name = dir.name

            if not (dir / "plugin.py").is_file():
                logger.warning(f"{_plugin_name} plugin does not contain a 'plugin.py' file. Skipping plugin initialization...")
                continue
            if not (dir / "metadata_template.toml").is_file():
                logger.warning(f"{_plugin_name} plugin does not contain a 'metadata_template.toml' file. Skipping plugin initialization...")
                continue
            try:
                _plugin_config_path: pathlib.Path = pathlib.Path.cwd() / _cfg.get(MumimoCfgFields.SETTINGS.PLUGINS.PLUGINS_CONFIG_PATH) / _plugin_name
                # Create the plugin's config directory if it does not exist and create the 'metadata.toml' from the template file.
                if not pathlib.Path.is_dir(_plugin_config_path):
                    pathlib.Path.mkdir(_plugin_config_path, parents=True, exist_ok=True)
                    logger.debug(f"Created config directory for '{_plugin_name}' plugin.")
                    shutil.copy(dir / "metadata_template.toml", _plugin_config_path / "metadata.toml")
                # If the plugin config directory already exists but the 'metadata.toml' file is missing, then skip plugin initialization.
                elif not (_plugin_config_path / "metadata.toml").is_file():
                    logger.warning(f"'{_plugin_name}' plugin does not contain a 'metadata_template.toml' file. Skipping plugin initialization...")
                    continue
            except IOError as exc:
                raise ServiceError(f"Unable to create config directory for '{_plugin_name}' plugin.", logger=logger) from exc

            _registered_plugin = __import__(f"{_plugin_name}.plugin", fromlist=["*"]).Plugin

            _plugin_commands: CommandCallbacks = CommandCallbacks()
            # Register all the commands belonging to this plugin.
            try:
                for command_name, command_value in _registered_plugin.command.all.items():
                    _plugin_commands.register_command(
                        callback_name=command_name,
                        plugin_name=_plugin_name,
                        command_func=command_value[0],
                        command_parameters=command_value[1],
                    )
                    logger.debug(f"Registered '{_plugin_name}.{command_name}.[{'|'.join(command_value[1])}]' plugin command.")
                settings.set_command_callbacks(_plugin_commands)
            except AttributeError as exc:
                raise ServiceError(
                    f"Unable to initialize '{_plugin_name}' plugin. The command attribute does not exist in the plugin class.", logger=logger
                ) from exc

            _plugin_cfg = Config(_plugin_config_path / "metadata.toml")
            _plugin_cmd_permissions = _plugin_cfg.get(PluginCfgFields.PLUGIN.COMMANDS.DEFAULT_PERMISSION_GROUPS, [])
            # Import the plugin to the database and associate it with the plugin commands.
            async with db_service.session() as session:
                _query = await session.execute(select(PluginTable).filter_by(name=_plugin_name))
                _db_plugin: Optional[PluginTable] = _query.scalar()
                _plugin_modified: bool = False
                if _db_plugin is not None:
                    logger.debug(f"Plugin '{_plugin_name}' already exists in the database. Skipping import...")
                else:
                    _db_plugin = PluginTable(name=_plugin_name)
                    _plugin_modified = True
                    logger.debug(f"Plugin '{_plugin_name}' not detected in the database. This plugin will be imported.")
                # Import plugin commands to the database with plugin-specified default permissions if the command does not already exist.
                _imported_cmd_count: int = 0
                for command_name, command_value in _registered_plugin.command.all.items():
                    _query = await session.execute(select(CommandTable).filter_by(name=command_name))
                    _command: Optional[CommandTable] = _query.scalar()
                    if _command is not None:
                        logger.debug(f"Command '{_plugin_name}.{command_name}' already exists in the database. Skipping import...")
                    else:
                        _command = CommandTable(name=command_name)
                        _command.permission_groups.extend(_plugin_cmd_permissions)
                        _db_plugin.commands.append(_command)
                        _imported_cmd_count += 1
                        _plugin_modified = True
                        logger.debug(f"Command '{_plugin_name}.{command_name}' not detected in the database. This command will be imported.")
                # Add the plugin and associated commands to the database if any modifications were detected since the previous run.
                if _plugin_modified:
                    session.add(_db_plugin)
                    await session.commit()
                    logger.debug(f"Imported plugin '{_plugin_name}' in the database with {_imported_cmd_count} new commands.")
                else:
                    logger.debug(
                        f"Plugin '{_plugin_name}' already exists in the database and was unmodified from the previous run. "
                        f"No new database imports conducted."
                    )

            _registered_plugins[_plugin_name] = _registered_plugin()

        sys.path.pop(0)
        logger.info("Initialized all plugins.")
