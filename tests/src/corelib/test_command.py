import pytest

from src.corelib.command import Command


class TestCommand:
    class TestCommandInit:
        def test_command_init_empty(self):
            cmd: Command = Command()
            assert cmd is not None
            assert cmd.actor == -1
            assert cmd.command is None
            assert cmd.parameters == []
            assert cmd.message == ""
            assert cmd.channel_id == -1
            assert cmd.session_id == -1

        def test_command_init_channel_id_is_none(self):
            cmd: Command = Command(channel_id=None)
            assert cmd.channel_id == -1

        def test_command_init_session_id_is_none(self):
            cmd: Command = Command(session_id=None)
            assert cmd.session_id == -1

    class TestCommandGetterSetters:
        @pytest.fixture(autouse=True)
        def cmd(self):
            return Command()

        def test_command_getter(self, cmd):
            assert cmd.command is None

        def test_command_setter(self, cmd):
            cmd.command = "test"
            assert cmd.command == "test"

        def test_message_getter(self, cmd):
            assert cmd.message == ""

        def test_message_setter(self, cmd):
            cmd.message = "test"
            assert cmd.message == "test"

        def test_parameters_getter(self, cmd):
            assert cmd.parameters == []

        def test_parameters_setter(self, cmd):
            cmd.parameters = ["test"]
            assert cmd.parameters == ["test"]

        def test_actor_getter(self, cmd):
            assert cmd.actor == -1

        def test_actor_setter(self, cmd):
            cmd.actor = 0
            assert cmd.actor == 0

        def test_channel_id_getter(self, cmd):
            assert cmd.channel_id == -1

        def test_channel_id_setter(self, cmd):
            cmd.channel_id = 0
            assert cmd.channel_id == 0

        def test_session_id_getter(self, cmd):
            assert cmd.session_id == -1

        def test_session_id_setter(self, cmd):
            cmd.session_id = 0
            assert cmd.session_id == 0

        def test_is_private_property_true(self, cmd):
            cmd.session_id = 0
            cmd.channel_id = -1
            assert cmd.is_private is True

        def test_is_private_property_false(self, cmd):
            cmd.session_id = -1
            cmd.channel_id = 0
            assert cmd.is_private is False
