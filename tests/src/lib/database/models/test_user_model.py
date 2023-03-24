import pytest
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_scoped_session

from src.lib.database.models.alias import AliasTable
from src.lib.database.models.permission_group import PermissionGroupTable
from src.lib.database.models.user import UserTable


class TestUserModel:
    @pytest.fixture(autouse=True)
    async def user(self) -> UserTable:
        user: UserTable = UserTable(
            name="test",
            permission_groups=[PermissionGroupTable(name="test")],
            aliases=[AliasTable(name="test", command="test")],
        )
        return user

    @pytest.mark.asyncio
    async def test_to_dict(self, user: UserTable) -> None:
        assert user.to_dict() == {
            "id": user.id,
            "name": user.name,
            "permission_groups": [x.to_dict() for x in user.permission_groups],
            "aliases": [alias.to_dict() for alias in user.aliases],
            "created_on": user.created_on,
            "updated_on": user.updated_on,
        }

    @pytest.mark.asyncio
    async def test_repr(self, user: UserTable) -> None:
        assert (
            str(user) == f"User(id={user.id!r}, name={user.name!r}, permission_groups={user.permission_groups}, "
            f"aliases={user.aliases!r}, created_on={user.created_on!r}, updated_on={user.updated_on!r})"
        )

    class TestModelIO:
        @pytest.mark.asyncio
        async def test_create_user(self):
            user: UserTable = UserTable(
                name="test",
                permission_groups=[PermissionGroupTable(name="test")],
                aliases=[AliasTable(name="test", command="test")],
            )
            assert user.name == "test"
            assert len(user.permission_groups) > 0
            assert isinstance(user.permission_groups[0], PermissionGroupTable) is True
            assert user.permission_groups[0].name == "test"
            assert len(user.aliases) > 0
            assert isinstance(user.aliases[0], AliasTable) is True
            assert user.aliases[0].name == "test"

        @pytest.mark.asyncio
        async def test_update_user(self, user: UserTable):
            assert user.name == "test"
            assert len(user.permission_groups) > 0
            assert isinstance(user.permission_groups[0], PermissionGroupTable) is True
            assert user.permission_groups[0].name == "test"
            assert len(user.aliases) > 0
            assert isinstance(user.aliases[0], AliasTable) is True
            assert user.aliases[0].name == "test"

            user.name = "new_test"
            user.permission_groups[0].name = "new_test"
            user.aliases[0].name = "new_test"
            assert user.name == "new_test"
            assert user.permission_groups[0].name == "new_test"
            assert len(user.aliases) > 0
            assert isinstance(user.aliases[0], AliasTable) is True
            assert user.aliases[0].name == "new_test"

    class TestDatabaseIO:
        @pytest.mark.asyncio
        async def test_add_user(self, user: UserTable, get_db_session_factory: async_scoped_session) -> None:
            session: async_scoped_session
            async with get_db_session_factory() as session:
                # Add new user "test"
                session.add(user)
                await session.commit()
                # Assert the "test" user exists
                _query = select(UserTable).filter_by(name="test")
                _result = await session.execute(_query)
                _result = _result.scalar()
                if _result is None:
                    pytest.fail("user not found, aborting test.")
                assert _result.name == "test"
                assert len(_result.permission_groups) > 0
                assert isinstance(_result.permission_groups[0], PermissionGroupTable) is True
                assert _result.permission_groups[0].name == "test"
                assert len(user.aliases) > 0
                assert isinstance(user.aliases[0], AliasTable) is True
                assert user.aliases[0].name == "test"
                # Assert the "test" permission group added by the user exists
                _query = select(PermissionGroupTable).filter_by(name="test")
                _result = await session.execute(_query)
                _result = _result.scalar()
                if _result is None:
                    pytest.fail("permission not found, aborting test.")
                assert _result.name == "test"
                # Assert the "test" alias added by the user exists
                _query = select(AliasTable).filter_by(name="test")
                _result = await session.execute(_query)
                _result = _result.scalar()
                if _result is None:
                    pytest.fail("alias not found, aborting test.")
                assert _result.name == "test"

        @pytest.mark.asyncio
        async def test_add_and_update_command(self, user: UserTable, get_db_session_factory: async_scoped_session) -> None:
            session: async_scoped_session
            async with get_db_session_factory() as session:
                # Add new user "test"
                session.add(user)
                await session.commit()
                # Assert the "test" user exists
                _query = select(UserTable).filter_by(name="test")
                _result = await session.execute(_query)
                _result = _result.scalar()
                if _result is None:
                    pytest.fail("user not found, aborting test.")
                assert _result.name == "test"
                assert len(_result.permission_groups) > 0
                assert isinstance(_result.permission_groups[0], PermissionGroupTable) is True
                assert _result.permission_groups[0].name == "test"
                assert len(_result.aliases) > 0
                assert isinstance(_result.aliases[0], AliasTable) is True
                assert _result.aliases[0].name == "test"
                # Update the "test" user name to "new_test"
                _result.name = "new_test"
                await session.commit()
                # Assert the "new_test" user group exists
                _query = select(UserTable).filter_by(name="new_test")
                _result = await session.execute(_query)
                _result = _result.scalar()
                if _result is None:
                    pytest.fail("updated user not found, aborting test.")
                assert _result.name == "new_test"

        @pytest.mark.asyncio
        async def test_add_and_delete_command(self, user: UserTable, get_db_session_factory: async_scoped_session) -> None:
            session: async_scoped_session
            async with get_db_session_factory() as session:
                # Add new user "test"
                session.add(user)
                await session.commit()
                # Assert the "test" user exists
                _query = select(UserTable).filter_by(name="test")
                _result = await session.execute(_query)
                _result = _result.scalar()
                if _result is None:
                    pytest.fail("user not found, aborting test.")
                assert _result.name == "test"
                assert len(_result.permission_groups) > 0
                assert isinstance(_result.permission_groups[0], PermissionGroupTable) is True
                assert _result.permission_groups[0].name == "test"
                assert len(_result.aliases) > 0
                assert isinstance(_result.aliases[0], AliasTable) is True
                assert _result.aliases[0].name == "test"
                # Delete the "test" user
                _query = delete(UserTable).where(UserTable.name == "test")
                _result = await session.execute(_query)
                await session.commit()
                # Assert the "test" user does not exist
                _query = select(UserTable).where(UserTable.name == "new_test")
                _result = await session.execute(_query)
                _result = _result.scalars().first()
                assert _result is None

    class TestFailures:
        @pytest.mark.asyncio
        @pytest.mark.xfail(raises=IntegrityError)
        async def test_create_invalid_user_fails_null_constraint(self, get_db_session_factory: async_scoped_session) -> None:
            session: async_scoped_session
            async with get_db_session_factory() as session:
                user: UserTable = UserTable()
                session.add(user)
                try:
                    await session.commit()
                except IntegrityError:
                    await session.rollback()

        @pytest.mark.asyncio
        @pytest.mark.xfail(raises=IntegrityError)
        async def test_create_invalid_user_fails_unique_constraint(self, get_db_session_factory: async_scoped_session):
            session: async_scoped_session
            async with get_db_session_factory() as session:
                user1: UserTable = UserTable(
                    name="test",
                    permission_groups=[PermissionGroupTable(name="test")],
                )
                session.add(user1)
                await session.flush()
                user2: UserTable = UserTable(
                    name="test",
                    permission_groups=[PermissionGroupTable(name="test")],
                )
                session.add(user2)
                try:
                    await session.commit()
                except IntegrityError:
                    await session.rollback()
