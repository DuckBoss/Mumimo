import asyncio
import contextlib
import logging
from typing import TYPE_CHECKING, AsyncGenerator, List, Optional, Tuple

import sqlalchemy_utils
from sqlalchemy import select
from sqlalchemy.exc import NoSuchModuleError
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, async_sessionmaker, create_async_engine

from ..constants import LogOutputIdentifiers, MumimoCfgFields
from ..exceptions import DatabaseServiceError
from ..lib.database import metadata
from ..lib.database.database_connection_parameters import DatabaseConnectionParameters
from ..lib.database.models.alias import AliasTable  # noqa
from ..lib.database.models.command import CommandTable  # noqa
from ..lib.database.models.permission_group import PermissionGroupTable  # noqa
from ..lib.database.models.plugin import PluginTable  # noqa
from ..lib.database.models.user import UserTable  # noqa
from ..lib.singleton import singleton
from ..settings import settings
from ..utils.parsers.db_url_parser import get_url

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)


@singleton
class DatabaseService:
    _engine: Optional["AsyncEngine"] = None
    _connection_parameters: Optional[DatabaseConnectionParameters] = None
    _session_factory: Optional[async_scoped_session] = None

    async def initialize_database(
        self,
        dialect: str,
        host: str,
        database: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        drivername: Optional[str] = None,
        query: Optional[str] = None,
    ) -> None:
        db_connection_opts: DatabaseConnectionParameters = DatabaseConnectionParameters(
            dialect=dialect,
            drivername=drivername,
            database=database,
            host=host,
            username=username,
            password=password,
            query=query,
        )
        await self.setup(db_connection_opts)
        await self.import_default_values()

    async def _import_default_permission_groups(self, cfg):
        logger.debug(f"[{LogOutputIdentifiers.DB_PERMISSIONS}]: Importing default permission groups...")
        _default_permission_groups: List[str] = cfg.get(MumimoCfgFields.SETTINGS.DATABASE.DEFAULT_PERMISSION_GROUPS, [])
        async with self.session() as session:
            for permission_group in _default_permission_groups:
                # Check if the permission group is a valid string:
                if not isinstance(permission_group, str) or permission_group.strip() == "":
                    logger.warning(
                        f"[{LogOutputIdentifiers.DB_PERMISSIONS}]: Unable to import default permission group. Invalid string - "
                        f"'{permission_group}'"
                    )
                    continue
                permission_group = permission_group.strip()
                # Check if the permission group already exists to prevent duplicate imports.
                exists = await session.execute(select(PermissionGroupTable).filter_by(name=permission_group))
                if len(exists.scalars().all()) > 0:
                    logger.debug(
                        f"[{LogOutputIdentifiers.DB_PERMISSIONS}]: Permission already exists. Skipped importing default permission group - "
                        f"'{permission_group}'"
                    )
                    continue
                # Add the new imported permission group.
                _new_permission: PermissionGroupTable = PermissionGroupTable(name=permission_group)
                session.add(_new_permission)
                await session.commit()
                logger.debug(f"[{LogOutputIdentifiers.DB_PERMISSIONS}]: Imported default permission group - '{permission_group}'")
            logger.debug(f"[{LogOutputIdentifiers.DB_PERMISSIONS}]: Finished adding default permission groups.")

    async def _import_default_aliases(self, cfg):
        logger.debug(f"[{LogOutputIdentifiers.DB_ALIASES}]: Importing default aliases...")
        _default_aliases: List[List[str]] = cfg.get(MumimoCfgFields.SETTINGS.DATABASE.DEFAULT_ALIASES, "")
        async with self.session() as session:
            for alias in _default_aliases:
                # Validate the alias parameters provided in the config file.
                if len(alias) != 3:
                    logger.warning(
                        f"[{LogOutputIdentifiers.DB_ALIASES}]: Invalid alias - unable to import default alias due to missing alias parameters. \
                                   Please check your config file."
                    )
                    continue
                if not isinstance(alias[0], str):
                    logger.warning(
                        f"[{LogOutputIdentifiers.DB_ALIASES}]: Invalid alias - unable to import default alias. \
                                   The alias name must be a string value."
                    )
                    continue
                if not isinstance(alias[1], str):
                    logger.warning(
                        f"[{LogOutputIdentifiers.DB_ALIASES}]: Invalid alias - unable to import default alias '{alias[0]}'. \
                                   The alias command must be a string value."
                    )
                    continue
                if not isinstance(alias[2], str):
                    logger.warning(
                        f"[{LogOutputIdentifiers.DB_ALIASES}]: Invalid alias - unable to import default alias '{alias[0]}'. \
                            The alias permission groups must be a comma-separated string value."
                    )
                    continue
                # Check if the alias already exists to prevent duplicate imports.
                _alias_exists = await session.execute(select(AliasTable).filter_by(name=alias[0]))
                if len(_alias_exists.scalars().all()) > 0:
                    logger.debug(f"[{LogOutputIdentifiers.DB_ALIASES}]: Alias '{alias[0]}' already exists. Skipped import.")
                    continue
                # Filter permissions that exist in the permission group table and add it to the new alias object.
                _new_alias: AliasTable = AliasTable(name=alias[0], command=alias[1])
                # Get the permissions string and separate into a list of strings.
                _alias_permission_groups: List[str] = [permission.strip() for permission in alias[2].split(",")]
                if not _alias_permission_groups:
                    logger.debug(f"[{LogOutputIdentifiers.DB_ALIASES}]: No permission groups added for alias - '{alias[0]}'")
                else:
                    _permissions_query = await session.execute(
                        select(PermissionGroupTable).filter(PermissionGroupTable.name.in_(_alias_permission_groups))
                    )
                    _all_matching_permissions = _permissions_query.scalars().all()
                    for permission_group in _all_matching_permissions:
                        _new_alias.permission_groups.append(permission_group)
                        logger.debug(
                            f"[{LogOutputIdentifiers.DB_ALIASES}]: Added permission group for imported default alias - "
                            f"'{alias[0]}':[{permission_group.name}]"
                        )
                # Do not attempt to add imported alias if no valid permission groups are found.
                if len(_new_alias.permission_groups) == 0:
                    logger.warning(f"[{LogOutputIdentifiers.DB_ALIASES}]: Unable to add default alias. No valid permission groups detected.")
                    continue
                # Add the new imported alias.
                session.add(_new_alias)
                await session.commit()
                logger.debug(f"[{LogOutputIdentifiers.DB_ALIASES}]: Imported default alias - '{alias[0]}'")

            logger.debug(f"[{LogOutputIdentifiers.DB_ALIASES}]: Finished adding default aliases.")

    async def import_default_values(self):
        if self._engine is None:
            raise DatabaseServiceError(
                f"[{LogOutputIdentifiers.DB}]: Cannot import default values. Database connection engine is not initialized.", logger=logger
            )
        _cfg = settings.get_mumimo_config()
        if _cfg is None:
            raise DatabaseServiceError(
                f"[{LogOutputIdentifiers.DB}]: Cannot import default values. The mumimo config has not been initialized.", logger=logger
            )

        # Import default permission groups:
        await self._import_default_permission_groups(_cfg)

        # Import default aliases:
        await self._import_default_aliases(_cfg)

    async def setup(self, connection_parameters: DatabaseConnectionParameters):
        # Ensure that there are no existing engine connections initialized.
        if self._engine is not None:
            raise DatabaseServiceError(
                f"[{LogOutputIdentifiers.DB}]: Connection engine is already initialized. Close the connection first.", logger=logger
            )

        # Validate connection parameters.
        if connection_parameters is None:
            raise DatabaseServiceError(f"[{LogOutputIdentifiers.DB}]: Connection parameters were not provided.", logger=logger)
        _validation_result: Tuple[bool, str] = await self._validate_connection_parameters(connection_parameters)
        if not _validation_result[0]:
            raise DatabaseServiceError(f"[{LogOutputIdentifiers.DB}]: Connection parameters are invalid - '{_validation_result[1]}'.", logger=logger)
        self._connection_parameters = connection_parameters

        # Create the database, initialize the async engine and create all missing tables.
        _create_db_url: str = get_url(self._connection_parameters, use_driver=False, use_database=False)
        _async_url: str = get_url(self._connection_parameters)
        try:
            if not sqlalchemy_utils.database_exists(_create_db_url):
                sqlalchemy_utils.create_database(_create_db_url)
            self._engine = create_async_engine(_async_url, echo=False)
            async with self._engine.begin() as conn:
                await conn.run_sync(metadata.Base.metadata.create_all)
        except NoSuchModuleError as exc:
            raise DatabaseServiceError(
                f"[{LogOutputIdentifiers.DB}]: Database connection dialect could not be found. Please check your dialect connection parameters.",
                logger=logger,
            ) from exc
        except Exception as exc:
            raise DatabaseServiceError(
                f"[{LogOutputIdentifiers.DB}]: Database could not be opened. Please check your connection parameters.",
                logger=logger,
            ) from exc

        # Initialize the async session factory with the initialized async engine.
        self._session_factory = async_scoped_session(
            session_factory=async_sessionmaker(self._engine, class_=AsyncSession, expire_on_commit=False),
            scopefunc=asyncio.current_task,
        )

    async def _validate_connection_parameters(self, connection_parameters: DatabaseConnectionParameters) -> Tuple[bool, str]:
        _check_credentials: bool = connection_parameters.password is None or connection_parameters.username is None
        _check_driver: bool = connection_parameters.drivername is None
        _check_query: bool = connection_parameters.query is None
        _check_database_name: bool = connection_parameters.database is None
        _validation_result: Tuple[bool, str] = connection_parameters.validate_parameters(
            no_database_name=_check_database_name,
            no_credentials=_check_credentials,
            no_driver=_check_driver,
            no_query=_check_query,
        )
        return _validation_result

    async def close(self, clean: bool = False) -> None:
        logger.debug(f"[{LogOutputIdentifiers.DB}]: Attempting to close mumimo database connection.")
        if self._engine is not None:
            await self._engine.dispose(close=True)
            if clean:
                self._connection_parameters = None
                self._session_factory = None
                self._engine = None
            logger.debug(f"[{LogOutputIdentifiers.DB}]: Mumimo database connection closed.")

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        if self._session_factory is None:
            raise DatabaseServiceError(
                f"[{LogOutputIdentifiers.DB}]: Unable to retrieve database session due to an uninitialized session factory.", logger=logger
            )
        async with self._session_factory() as session:
            try:
                yield session
            except Exception as exc:
                await session.rollback()
                raise DatabaseServiceError(
                    f"[{LogOutputIdentifiers.DB}]: Encountered an error with the database session. Rolled back changes.", logger=logger
                ) from exc
            finally:
                await session.close()
