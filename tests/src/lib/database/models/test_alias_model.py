import pytest
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_scoped_session

from src.lib.database.models.alias import AliasTable
from src.lib.database.models.permission_group import PermissionGroupTable


class TestCommandModel:
    @pytest.fixture(autouse=True)
    async def alias(self) -> AliasTable:
        alias: AliasTable = AliasTable(
            name="test",
            command="test",
            permission_groups=[PermissionGroupTable(name="test")],
        )
        return alias

    @pytest.mark.asyncio
    async def test_to_dict(self, alias: AliasTable) -> None:
        assert alias.to_dict() == {
            "id": alias.id,
            "name": alias.name,
            "command": alias.command,
            "permission_groups": [x.to_dict() for x in alias.permission_groups],
            "created_on": alias.created_on,
            "updated_on": alias.updated_on,
        }

    @pytest.mark.asyncio
    async def test_repr(self, alias: AliasTable) -> None:
        assert (
            str(alias) == f"Alias(id={alias.id!r}, name={alias.name!r}, command={alias.command!r}, permission_groups={alias.permission_groups}, "
            f"created_on={alias.created_on!r}, updated_on={alias.updated_on!r})"
        )

    class TestModelIO:
        @pytest.mark.asyncio
        async def test_create_alias(self):
            alias: AliasTable = AliasTable(
                name="test",
                command="test",
                permission_groups=[PermissionGroupTable(name="test")],
            )
            assert alias.name == "test"
            assert alias.command == "test"
            assert len(alias.permission_groups) > 0
            assert isinstance(alias.permission_groups[0], PermissionGroupTable) is True
            assert alias.permission_groups[0].name == "test"

        @pytest.mark.asyncio
        async def test_update_alias(self, alias: AliasTable):
            assert alias.name == "test"
            assert alias.command == "test"
            assert len(alias.permission_groups) > 0
            assert isinstance(alias.permission_groups[0], PermissionGroupTable) is True
            assert alias.permission_groups[0].name == "test"
            alias.name = "new_test"
            alias.command = "new_test"
            alias.permission_groups[0].name = "new_test"
            assert alias.name == "new_test"
            assert alias.command == "new_test"
            assert alias.permission_groups[0].name == "new_test"

    class TestDatabaseIO:
        @pytest.mark.asyncio
        async def test_add_alias(self, alias: AliasTable, get_db_session_factory: async_scoped_session) -> None:
            session: async_scoped_session
            async with get_db_session_factory() as session:
                # Add new alias "test"
                session.add(alias)
                await session.commit()
                # Assert the "test" alias exists
                _query = select(AliasTable).filter_by(name="test")
                _result = await session.execute(_query)
                _result = _result.scalar()
                if _result is None:
                    pytest.fail("alias not found, aborting test.")
                assert _result.name == "test"
                assert _result.command == "test"
                assert len(_result.permission_groups) > 0
                assert isinstance(_result.permission_groups[0], PermissionGroupTable) is True
                assert _result.permission_groups[0].name == "test"
                # Assert the "test" permission group added by the alias exists
                _query = select(PermissionGroupTable).filter_by(name="test")
                _result = await session.execute(_query)
                _result = _result.scalar()
                if _result is None:
                    pytest.fail("permission group not found, aborting test.")
                assert _result.name == "test"

        @pytest.mark.asyncio
        async def test_add_and_update_alias(self, alias: AliasTable, get_db_session_factory: async_scoped_session) -> None:
            session: async_scoped_session
            async with get_db_session_factory() as session:
                # Add new alias "test"
                session.add(alias)
                await session.commit()
                # Assert the "test" alias exists
                _query = select(AliasTable).filter_by(name="test")
                _result = await session.execute(_query)
                _result = _result.scalar()
                if _result is None:
                    pytest.fail("alias not found, aborting test.")
                assert _result.name == "test"
                assert _result.command == "test"
                assert len(_result.permission_groups) > 0
                assert isinstance(_result.permission_groups[0], PermissionGroupTable) is True
                assert _result.permission_groups[0].name == "test"
                # Update the "test" alias name and command to "new_test"
                _result.name = "new_test"
                _result.command = "new_test"
                await session.commit()
                # Assert the "new_test" alias group exists
                _query = select(AliasTable).where(AliasTable.name == "new_test")
                _result = await session.execute(_query)
                _result = _result.scalars().first()
                if _result is None:
                    pytest.fail("updated command not found, aborting test.")
                assert _result.name == "new_test"
                assert _result.command == "new_test"

        @pytest.mark.asyncio
        async def test_add_and_delete_alias(self, alias: AliasTable, get_db_session_factory: async_scoped_session) -> None:
            session: async_scoped_session
            async with get_db_session_factory() as session:
                # Add new alias "test"
                session.add(alias)
                await session.commit()
                # Assert the "test" alias exists
                _query = select(AliasTable).filter_by(name="test")
                _result = await session.execute(_query)
                _result = _result.scalar()
                if _result is None:
                    pytest.fail("command not found, aborting test.")
                assert _result.name == "test"
                assert _result.command == "test"
                assert len(_result.permission_groups) > 0
                assert isinstance(_result.permission_groups[0], PermissionGroupTable) is True
                assert _result.permission_groups[0].name == "test"
                # Delete the "test" alias
                _query = delete(AliasTable).where(AliasTable.name == "test")
                _result = await session.execute(_query)
                await session.commit()
                # Assert the "test" alias group does not exist
                _query = select(AliasTable).where(AliasTable.name == "new_test")
                _result = await session.execute(_query)
                _result = _result.scalars().first()
                assert _result is None

    class TestFailures:
        @pytest.mark.asyncio
        @pytest.mark.xfail(raises=IntegrityError)
        async def test_create_invalid_alias_fails_null_constraints(self, get_db_session_factory: async_scoped_session) -> None:
            session: async_scoped_session
            async with get_db_session_factory() as session:
                alias: AliasTable = AliasTable()
                session.add(alias)
                try:
                    await session.commit()
                except IntegrityError:
                    await session.rollback()

        @pytest.mark.asyncio
        @pytest.mark.xfail(raises=IntegrityError)
        async def test_create_invalid_alias_fails_null_constraint_name(self, get_db_session_factory: async_scoped_session) -> None:
            session: async_scoped_session
            async with get_db_session_factory() as session:
                alias: AliasTable = AliasTable(name="test")
                session.add(alias)
                try:
                    await session.commit()
                except IntegrityError:
                    await session.rollback()

        @pytest.mark.asyncio
        @pytest.mark.xfail(raises=IntegrityError)
        async def test_create_invalid_alias_fails_null_constraint_command(self, get_db_session_factory: async_scoped_session) -> None:
            session: async_scoped_session
            async with get_db_session_factory() as session:
                alias: AliasTable = AliasTable(command="test")
                session.add(alias)
                try:
                    await session.commit()
                except IntegrityError:
                    await session.rollback()

        @pytest.mark.asyncio
        @pytest.mark.xfail(raises=IntegrityError)
        async def test_create_invalid_alias_fails_unique_constraint(self, get_db_session_factory: async_scoped_session):
            session: async_scoped_session
            async with get_db_session_factory() as session:
                alias1: AliasTable = AliasTable(
                    name="test",
                    command="test",
                    permission_groups=[PermissionGroupTable(name="test")],
                )
                session.add(alias1)
                await session.flush()
                alias2: AliasTable = AliasTable(
                    name="test",
                    command="test",
                    permission_groups=[PermissionGroupTable(name="test")],
                )
                session.add(alias2)
                try:
                    await session.commit()
                except IntegrityError:
                    await session.rollback()
