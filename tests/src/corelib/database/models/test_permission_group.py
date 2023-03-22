from typing import AsyncGenerator

import asyncio

import pytest
import sqlalchemy_utils
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, async_sessionmaker, create_async_engine
from sqlalchemy.exc import IntegrityError

from src.corelib.database.metadata import Base
from src.corelib.database.database_connection_parameters import DatabaseConnectionParameters
from src.corelib.database.models.permission_group import PermissionGroupTable  # noqa
from src.utils.parsers.db_url_parser import get_url

import logging

logger = logging.getLogger(__name__)


class TestPermissionGroup:
    @pytest.fixture(autouse=True)
    async def get_session_factory(self) -> AsyncGenerator[async_scoped_session, None]:
        # Imports are required here so tables can be created for tests.
        from src.corelib.database.models.alias import AliasTable  # noqa
        from src.corelib.database.models.command import CommandTable  # noqa
        from src.corelib.database.models.user import UserTable  # noqa
        from src.corelib.database.models.plugin import PluginTable  # noqa

        _dialect: str = "sqlite"
        _host: str = "tests/data/generated/mumimo_test.db"
        _drivername: str = "aiosqlite"
        self._connection_parameters = DatabaseConnectionParameters(
            dialect=_dialect,
            host=_host,
            drivername=_drivername,
        )
        _create_db_url: str = get_url(self._connection_parameters, use_driver=False, use_database=False)
        _async_url: str = get_url(self._connection_parameters)
        logger.warning(_create_db_url)
        logger.warning(_async_url)
        if not sqlalchemy_utils.database_exists(_create_db_url):
            sqlalchemy_utils.create_database(_create_db_url)
        self._engine = create_async_engine(_async_url, echo=False)
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self._session_factory = async_scoped_session(
            session_factory=async_sessionmaker(self._engine, class_=AsyncSession, expire_on_commit=False),
            scopefunc=asyncio.current_task,
        )
        yield self._session_factory
        await self.teardown_engine()

    async def teardown_engine(self):
        if self._engine is not None:
            await self._engine.dispose(close=True)
            self._connection_parameters = None
            self._session_factory = None
            self._engine = None

    @pytest.mark.asyncio
    async def test_create_permission_group(self, get_session_factory: async_scoped_session):
        if get_session_factory is None:
            pytest.fail("Session factory not initialized for this test!")

        session: async_scoped_session
        permission_group: PermissionGroupTable = PermissionGroupTable(name="test")
        async with get_session_factory() as session:
            # Add permission group "test"
            session.add(permission_group)
            await session.commit()
            # Assert the "test" permission group exists
            _query = select(PermissionGroupTable).filter_by(name="test")
            _result = await session.execute(_query)
            _result = _result.scalar()
            if _result is None:
                pytest.fail("permission not found, aborting test.")
            assert _result.name == "test"

    @pytest.mark.asyncio
    async def test_create_and_update_permission_group(self, get_session_factory: async_scoped_session):
        if get_session_factory is None:
            pytest.fail("Session factory not initialized for this test!")

        session: async_scoped_session
        async with get_session_factory() as session:
            # Add permission group "test"
            permission_group: PermissionGroupTable = PermissionGroupTable(name="test")
            session.add(permission_group)
            await session.commit()
            # Assert the "test" permission group exists
            _query = select(PermissionGroupTable).where(PermissionGroupTable.name == "test")
            _row = await session.execute(_query)
            _result = _row.scalar()
            if _result is None:
                pytest.fail("permission not found, aborting test.")
            assert _result.name == "test"
            # Update the "test" permission group name to "new_test"
            _result.name = "new_test"
            await session.commit()
            # Assert the "new_test" permission group exists.
            _query = select(PermissionGroupTable).where(PermissionGroupTable.name == "new_test")
            _result = await session.execute(_query)
            _result = _result.scalars().first()
            if _result is None:
                pytest.fail("updated permission not found, aborting test.")
            assert _result.name == "new_test"
