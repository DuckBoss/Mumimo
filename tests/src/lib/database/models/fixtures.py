import asyncio
from typing import AsyncGenerator

import pytest
import sqlalchemy_utils
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, async_sessionmaker, create_async_engine

from src.lib.database.database_connection_parameters import DatabaseConnectionParameters
from src.lib.database.metadata import Base

# Imports are required here so tables can be created for tests.
from src.lib.database.models.alias import AliasTable  # noqa
from src.lib.database.models.command import CommandTable  # noqa
from src.lib.database.models.permission_group import PermissionGroupTable  # noqa
from src.lib.database.models.plugin import PluginTable  # noqa
from src.lib.database.models.user import UserTable  # noqa
from src.utils.parsers.db_url_parser import get_url


@pytest.fixture(scope="function")
async def get_db_session_factory() -> AsyncGenerator[async_scoped_session, None]:
    _dialect: str = "sqlite"
    _host: str = "tests/data/generated/mumimo_test.db"
    _drivername: str = "aiosqlite"
    _connection_parameters = DatabaseConnectionParameters(
        dialect=_dialect,
        host=_host,
        drivername=_drivername,
    )
    _create_db_url: str = get_url(_connection_parameters, use_driver=False, use_database=False)
    _async_url: str = get_url(_connection_parameters)
    if not sqlalchemy_utils.database_exists(_create_db_url):
        sqlalchemy_utils.create_database(_create_db_url)
    _engine = create_async_engine(_async_url, echo=False)
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    _session_factory = async_scoped_session(
        session_factory=async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False),
        scopefunc=asyncio.current_task,
    )
    yield _session_factory
    # Teardown:
    if _engine is not None:
        await _engine.dispose(close=True)
        _connection_parameters = None
        _session_factory = None
        _engine = None
