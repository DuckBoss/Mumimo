from typing import List, Optional

import pytest

from src.corelib.command import Command
from src.corelib.command_history import CommandHistory


class TestCommandHistory:
    @pytest.fixture(autouse=True)
    def mock_cmd_history_list(self) -> List[Command]:
        history: List[Command] = [
            Command("test_1", ["param_1", "param_2"], "test_msg_1"),
            Command("test_2", ["param_1", "param_2"], "test_msg_2"),
            Command("test_3", ["param_1", "param_2"], "test_msg_3"),
            Command("test_4", ["param_1", "param_2"], "test_msg_4"),
        ]
        return history

    @pytest.fixture(autouse=True)
    def mock_empty_cmd_history(self) -> CommandHistory:
        history: CommandHistory = CommandHistory()
        return history

    @pytest.fixture(autouse=True)
    def mock_filled_cmd_history(self, mock_cmd_history_list) -> CommandHistory:
        history: CommandHistory = CommandHistory()
        for cmd in mock_cmd_history_list:
            history.add(cmd)
        return history

    class TestCommandHistoryInit:
        def test_command_history_init(self) -> None:
            history: CommandHistory = CommandHistory()
            assert history is not None

        def test_command_history_init_with_limit(self) -> None:
            history: CommandHistory = CommandHistory(history_limit=10)
            assert history is not None
            assert history.limit == 10

        def test_command_history_init_with_invalid_limit(self) -> None:
            history: CommandHistory = CommandHistory(history_limit=-5)
            assert history is not None
            assert history.limit == CommandHistory.DEFAULT_HISTORY_LIMIT

        def test_command_history_init_with_none_limit(self) -> None:
            history: CommandHistory = CommandHistory(history_limit=None)
            assert history is not None
            assert history.limit == CommandHistory.DEFAULT_HISTORY_LIMIT

    class TestCommandHistoryProperties:
        def test_command_history_history_property(self, mock_filled_cmd_history: CommandHistory) -> None:
            history: CommandHistory = mock_filled_cmd_history
            assert history.history is not None

        def test_command_history_length_property(self, mock_filled_cmd_history: CommandHistory, mock_cmd_history_list: List[Command]) -> None:
            history: CommandHistory = mock_filled_cmd_history
            assert history.length == len(mock_cmd_history_list)

        def test_command_history_limit_property(self, mock_empty_cmd_history: CommandHistory) -> None:
            history: CommandHistory = mock_empty_cmd_history
            assert history.limit == mock_empty_cmd_history.DEFAULT_HISTORY_LIMIT

    class TestCommandHistorySetters:
        def test_command_history_limit_setter_valid_limit(self, mock_empty_cmd_history: CommandHistory) -> None:
            history: CommandHistory = mock_empty_cmd_history
            history.limit = 10
            assert history.limit == 10

        def test_command_history_limit_setter_invalid_limit(self, mock_empty_cmd_history: CommandHistory) -> None:
            history: CommandHistory = mock_empty_cmd_history
            history.limit = -5
            assert history.limit == mock_empty_cmd_history.DEFAULT_HISTORY_LIMIT

    class TestCommandHistoryMethods:
        class TestGetLast:
            def test_command_history_get_last_valid(self, mock_filled_cmd_history: CommandHistory) -> None:
                history: CommandHistory = mock_filled_cmd_history
                history.add(Command("test_5", message="test_msg_5"))
                cmd_result: List[Command] = history.get_last(1)
                assert cmd_result
                assert cmd_result[0].command == "test_5"

            def test_command_history_get_last_invalid_last_n(self, mock_filled_cmd_history: CommandHistory) -> None:
                history: CommandHistory = mock_filled_cmd_history
                cmd_result: List[Command] = history.get_last(0)
                assert not cmd_result

            def test_command_history_get_last_with_empty_history(self, mock_empty_cmd_history: CommandHistory) -> None:
                history: CommandHistory = mock_empty_cmd_history
                cmd_result: List[Command] = history.get_last(0)
                assert not cmd_result

        class TestAdd:
            def test_command_history_add(self, mock_filled_cmd_history) -> None:
                history: CommandHistory = mock_filled_cmd_history
                cmd_result: Optional[Command] = history.add(Command("test_5", message="test_msg_5"))
                assert cmd_result is not None
                assert cmd_result.command == "test_5"

            def test_command_history_add_above_limit_fails(self, mock_filled_cmd_history) -> None:
                history: CommandHistory = mock_filled_cmd_history
                mock_filled_cmd_history.limit = mock_filled_cmd_history.length
                cmd_result: Optional[Command] = history.add(Command("test_5", message="test_msg_5"))
                assert cmd_result is None

        class TestPop:
            def test_command_history_pop_valid_index(self, mock_filled_cmd_history: CommandHistory) -> None:
                history: CommandHistory = mock_filled_cmd_history
                cmd_result: Optional[Command] = history.pop(0)
                assert cmd_result is not None
                assert cmd_result.command == "test_1"

            def test_command_history_pop_invalid_index(self, mock_filled_cmd_history: CommandHistory) -> None:
                history: CommandHistory = mock_filled_cmd_history
                cmd_result: Optional[Command] = history.pop(999)
                assert cmd_result is None

        class TestClear:
            def test_command_history_clear(self, mock_filled_cmd_history) -> None:
                history: CommandHistory = mock_filled_cmd_history
                history.clear()
                assert len(history.history) == 0
