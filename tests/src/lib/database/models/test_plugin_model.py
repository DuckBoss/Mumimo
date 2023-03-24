import pytest
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_scoped_session

from src.lib.database.models.command import CommandTable
from src.lib.database.models.plugin import PluginTable


class TestPluginModel:
    @pytest.fixture(autouse=True)
    async def plugin(self):
        plugin: PluginTable = PluginTable(
            name="test",
            commands=[CommandTable(name="test")],
        )
        return plugin

    @pytest.mark.asyncio
    async def test_to_dict(self, plugin: PluginTable) -> None:
        assert plugin.to_dict() == {
            "id": plugin.id,
            "name": plugin.name,
            "commands": [x.to_dict() for x in plugin.commands],
            "created_on": plugin.created_on,
            "updated_on": plugin.updated_on,
        }

    @pytest.mark.asyncio
    async def test_repr(self, plugin: PluginTable) -> None:
        assert (
            str(plugin) == f"Plugin(id={plugin.id!r}, name={plugin.name!r}, commands={plugin.commands}, "
            f"created_on={plugin.created_on!r}, updated_on={plugin.updated_on!r})"
        )

    class TestModelIO:
        @pytest.mark.asyncio
        async def test_create_plugin(self):
            plugin: PluginTable = PluginTable(
                name="test",
                commands=[CommandTable(name="test")],
            )
            assert plugin.name == "test"
            assert len(plugin.commands) > 0
            assert isinstance(plugin.commands[0], CommandTable) is True
            assert plugin.commands[0].name == "test"

        @pytest.mark.asyncio
        async def test_update_plugin(self, plugin: PluginTable):
            assert plugin.name == "test"
            assert len(plugin.commands) > 0
            assert isinstance(plugin.commands[0], CommandTable) is True
            assert plugin.commands[0].name == "test"
            plugin.name = "new_test"
            plugin.commands[0].name = "new_test"
            assert plugin.name == "new_test"
            assert plugin.commands[0].name == "new_test"

    class TestDatabaseIO:
        @pytest.mark.asyncio
        async def test_add_plugin(self, plugin: PluginTable, get_db_session_factory: async_scoped_session) -> None:
            session: async_scoped_session
            async with get_db_session_factory() as session:
                # Add new plugin "test"
                session.add(plugin)
                await session.commit()
                # Assert the "test" plugin exists
                _query = select(PluginTable).filter_by(name="test")
                _result = await session.execute(_query)
                _result = _result.scalar()
                if _result is None:
                    pytest.fail("plugin not found, aborting test.")
                assert _result.name == "test"
                assert len(_result.commands) > 0
                assert isinstance(_result.commands[0], CommandTable) is True
                assert _result.commands[0].name == "test"
                # Assert the "test" command added by the plugin exists
                _query = select(CommandTable).filter_by(name="test")
                _result = await session.execute(_query)
                _result = _result.scalar()
                if _result is None:
                    pytest.fail("command not found, aborting test.")
                assert _result.name == "test"

        @pytest.mark.asyncio
        async def test_add_and_update_plugin(self, plugin: PluginTable, get_db_session_factory: async_scoped_session) -> None:
            session: async_scoped_session
            async with get_db_session_factory() as session:
                # Add new plugin "test"
                session.add(plugin)
                await session.commit()
                # Assert the "test" plugin exists
                _query = select(PluginTable).filter_by(name="test")
                _result = await session.execute(_query)
                _result = _result.scalar()
                if _result is None:
                    pytest.fail("plugin not found, aborting test.")
                assert _result.name == "test"
                assert len(_result.commands) > 0
                assert isinstance(_result.commands[0], CommandTable) is True
                assert _result.commands[0].name == "test"
                # Update the "test" plugin name to "new_test"
                _result.name = "new_test"
                await session.commit()
                # Assert the "new_test" plugin group exists
                _query = select(PluginTable).where(PluginTable.name == "new_test")
                _result = await session.execute(_query)
                _result = _result.scalars().first()
                if _result is None:
                    pytest.fail("updated plugin not found, aborting test.")
                assert _result.name == "new_test"

        @pytest.mark.asyncio
        async def test_add_and_delete_plugin(self, plugin: PluginTable, get_db_session_factory: async_scoped_session) -> None:
            session: async_scoped_session
            async with get_db_session_factory() as session:
                session.add(plugin)
                await session.commit()
                # Assert the "test" plugin exists
                _query = select(PluginTable).filter_by(name="test")
                _result = await session.execute(_query)
                _result = _result.scalar()
                if _result is None:
                    pytest.fail("plugin not found, aborting test.")
                assert _result.name == "test"
                assert len(_result.commands) > 0
                assert isinstance(_result.commands[0], CommandTable) is True
                assert _result.commands[0].name == "test"
                # Delete the "test" plugin
                _query = delete(PluginTable).where(PluginTable.name == "test")
                _result = await session.execute(_query)
                await session.commit()
                # Assert the "test" plugin does not exist
                _query = select(PluginTable).where(PluginTable.name == "new_test")
                _result = await session.execute(_query)
                _result = _result.scalars().first()
                assert _result is None

    class TestFailures:
        @pytest.mark.asyncio
        @pytest.mark.xfail(raises=IntegrityError)
        async def test_create_invalid_plugin_fails_null_constraint(self, get_db_session_factory: async_scoped_session) -> None:
            session: async_scoped_session
            async with get_db_session_factory() as session:
                plugin: PluginTable = PluginTable()
                session.add(plugin)
                try:
                    await session.commit()
                except IntegrityError:
                    await session.rollback()

        @pytest.mark.asyncio
        @pytest.mark.xfail(raises=IntegrityError)
        async def test_create_invalid_plugin_fails_unique_constraint(self, get_db_session_factory: async_scoped_session):
            session: async_scoped_session
            async with get_db_session_factory() as session:
                plugin1: PluginTable = PluginTable(
                    name="test",
                    commands=[CommandTable(name="test")],
                )
                session.add(plugin1)
                await session.flush()
                plugin2: PluginTable = PluginTable(
                    name="test",
                    commands=[CommandTable(name="test2")],
                )
                session.add(plugin2)
                try:
                    await session.commit()
                except IntegrityError:
                    await session.rollback()
