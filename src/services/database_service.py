import asyncio
import contextlib
import logging
from typing import TYPE_CHECKING, AsyncGenerator, List, Optional

import sqlalchemy_utils
from sqlalchemy import select
from sqlalchemy.exc import NoSuchModuleError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, async_sessionmaker, create_async_engine

from ..constants import MumimoCfgFields
from ..corelib.database import metadata
from ..corelib.database.database_connection_parameters import DatabaseConnectionParameters
from ..corelib.database.models.permission_group import PermissionGroupTable  # noqa

# Import models:
from ..corelib.database.models.user import UserTable  # noqa
from ..corelib.singleton import singleton
from ..exceptions import DatabaseServiceError
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
        database: str,
        host: str,
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

    async def import_default_values(self):
        if self._engine is None:
            raise DatabaseServiceError("Database cannot import default values: database connection engine is not initialized.", logger=logger)
        _cfg = settings.get_mumimo_config()
        if _cfg is None:
            raise DatabaseServiceError("Database cannot import default values: the mumimo config has not been initialized.", logger=logger)

        # Import default permission groups:
        _default_permission_groups: List[str] = _cfg.get(MumimoCfgFields.SETTINGS.DATABASE.DEFAULT_PERMISSION_GROUPS, [])
        async with self.session() as session:
            for permission_group in _default_permission_groups:
                exists = await session.execute(select(PermissionGroupTable).filter_by(name=permission_group))
                if len(exists.scalars().all()) > 0:
                    logger.debug(f"Already exists: skipped importing default permission group - '{permission_group}'")
                    continue
                group: PermissionGroupTable = PermissionGroupTable(name=permission_group)
                session.add(group)
                await session.commit()
                logger.debug(f"Database: imported default permission group - '{permission_group}'")
            logger.debug("Database: Added all default permission groups.")

    async def setup(self, connection_params: DatabaseConnectionParameters):
        if self._engine is not None:
            raise DatabaseServiceError("Database connection engine is already initialized. Close the connection first.", logger=logger)
        if connection_params is None:
            raise DatabaseServiceError("Database connection parameters were not provided.", logger=logger)
        _check_credentials: bool = connection_params.password is None
        _check_driver: bool = connection_params.drivername is None
        _check_query: bool = connection_params.query is None
        _check_database_name: bool = connection_params.database is None
        _validation_result = connection_params.validate_parameters(
            no_database_name=_check_database_name,
            no_credentials=_check_credentials,
            no_driver=_check_driver,
            no_query=_check_query,
        )
        if not _validation_result[0]:
            raise DatabaseServiceError(f"Database connection parameters are invalid: {_validation_result[1]}", logger=logger)

        self._connection_parameters = connection_params
        _create_db_url: str = get_url(self._connection_parameters, use_driver=False, use_database=False)
        _async_url: str = get_url(self._connection_parameters)
        try:
            if not sqlalchemy_utils.database_exists(_create_db_url):
                sqlalchemy_utils.create_database(_create_db_url)
            self._engine = create_async_engine(_async_url, echo=False)
            async with self._engine.begin() as conn:
                await conn.run_sync(metadata.Base.metadata.create_all)

        except OperationalError as exc:
            raise DatabaseServiceError(
                f"Database could not be opened. Please check your connection parameters. \
                    \nConnection URLs: \ncreate_db_url:{_create_db_url}\nconnection_url:{_async_url}",
                logger=logger,
            ) from exc
        except NoSuchModuleError as exc:
            raise DatabaseServiceError(
                f"Database connection dialect could not be found. Please check your connection parameters. \
                    \nConnection URLs: \ncreate_db_url:{_create_db_url}\nconnection_url:{_async_url}",
                logger=logger,
            ) from exc
        except Exception as exc:
            raise DatabaseServiceError(
                f"Database connection engine failed to initialize. \nConnection URLs: \
                    \ncreate_db_url:{_create_db_url}\nconnection_url:{_async_url}",
                logger=logger,
            ) from exc

        self._session_factory = async_scoped_session(
            session_factory=async_sessionmaker(self._engine, class_=AsyncSession, expire_on_commit=False),
            scopefunc=asyncio.current_task,
        )

    async def close(self, clean: bool = False) -> None:
        logger.debug("Attempting to close mumimo database connection.")
        if self._engine is not None:
            await self._engine.dispose(close=True)
            if clean:
                self._connection_parameters = None
                self._session_factory = None
                self._engine = None
            logger.debug("Mumimo database connection closed.")

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        if self._session_factory is None:
            raise DatabaseServiceError("Unable to retrieve database session due to an uninitialized session factory.", logger=logger)
        async with self._session_factory() as session:
            try:
                yield session
            except Exception as exc:
                await session.rollback()
                raise DatabaseServiceError("Encountered an error with the database session. Rolled back changes.", logger=logger) from exc
            finally:
                await session.close()
