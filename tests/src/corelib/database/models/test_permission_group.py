import pytest
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_scoped_session

from src.corelib.database.models.permission_group import PermissionGroupTable  # noqa


class TestPermissionGroup:
    @pytest.mark.asyncio
    async def test_to_dict(self) -> None:
        permission_group: PermissionGroupTable = PermissionGroupTable(name="test")
        assert permission_group.to_dict() == {
            "id": permission_group.id,
            "name": permission_group.name,
            "created_on": permission_group.created_on,
            "updated_on": permission_group.updated_on,
        }

    @pytest.mark.asyncio
    async def test_repr(self) -> None:
        permission_group: PermissionGroupTable = PermissionGroupTable(name="test")
        assert (
            str(permission_group)
            == f"PermissionGroup(id={permission_group.id!r}, name={permission_group.name!r}, \
            created_on={permission_group.created_on!r}, updated_on={permission_group.updated_on!r})"
        )

    class TestModelIO:
        @pytest.mark.asyncio
        async def test_create_permission_group(self):
            permission_group: PermissionGroupTable = PermissionGroupTable(name="test")
            assert permission_group.name == "test"

        @pytest.mark.asyncio
        async def test_create_and_update_permission_group(self):
            permission_group: PermissionGroupTable = PermissionGroupTable(name="test")
            assert permission_group.name == "test"
            permission_group.name = "new_test"
            assert permission_group.name == "new_test"

    class TestDatabaseIO:
        @pytest.mark.asyncio
        async def test_add_permission_group(self, get_db_session_factory: async_scoped_session):
            if get_db_session_factory is None:
                pytest.fail("Session factory not initialized for this test!")

            session: async_scoped_session
            permission_group: PermissionGroupTable = PermissionGroupTable(name="test")
            async with get_db_session_factory() as session:
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
        async def test_add_and_update_permission_group(self, get_db_session_factory: async_scoped_session):
            if get_db_session_factory is None:
                pytest.fail("Session factory not initialized for this test!")

            session: async_scoped_session
            async with get_db_session_factory() as session:
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
                # Assert the "new_test" permission group exists
                _query = select(PermissionGroupTable).where(PermissionGroupTable.name == "new_test")
                _result = await session.execute(_query)
                _result = _result.scalars().first()
                if _result is None:
                    pytest.fail("updated permission not found, aborting test.")
                assert _result.name == "new_test"

        @pytest.mark.asyncio
        async def test_add_and_delete_permission_group(self, get_db_session_factory: async_scoped_session):
            if get_db_session_factory is None:
                pytest.fail("Session factory not initialized for this test!")

            session: async_scoped_session
            async with get_db_session_factory() as session:
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
                # Delete the "test" permission group
                _query = delete(PermissionGroupTable).where(PermissionGroupTable.name == "test")
                _result = await session.execute(_query)
                await session.commit()
                # Assert the "new_test" permission group does not exist
                _query = select(PermissionGroupTable).where(PermissionGroupTable.name == "test")
                _result = await session.execute(_query)
                _result = _result.scalars().first()
                assert _result is None

    class TestFailures:
        @pytest.mark.asyncio
        @pytest.mark.xfail(raises=IntegrityError)
        async def test_create_invalid_permission_group_fails_null_constraint(self, get_db_session_factory: async_scoped_session):
            if get_db_session_factory is None:
                pytest.fail("Session factory not initialized for this test!")

            session: async_scoped_session
            async with get_db_session_factory() as session:
                permission_group: PermissionGroupTable = PermissionGroupTable()
                session.add(permission_group)
                try:
                    await session.commit()
                except IntegrityError:
                    await session.rollback()

        @pytest.mark.asyncio
        @pytest.mark.xfail(raises=IntegrityError)
        async def test_create_invalid_permission_group_fails_unique_constraint(self, get_db_session_factory: async_scoped_session):
            if get_db_session_factory is None:
                pytest.fail("Session factory not initialized for this test!")

            session: async_scoped_session
            async with get_db_session_factory() as session:
                permission_group1: PermissionGroupTable = PermissionGroupTable(name="test")
                session.add(permission_group1)
                await session.flush()
                permission_group2: PermissionGroupTable = PermissionGroupTable(name="test")
                session.add(permission_group2)
                try:
                    await session.commit()
                except IntegrityError:
                    await session.rollback()
