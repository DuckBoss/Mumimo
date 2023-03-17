import pytest

from typing import Tuple
from src.murmur_connection import MurmurConnection


class TestMurmurConnectionSingleton:
    @pytest.fixture(autouse=True)
    def murmur_singletons(self) -> Tuple[MurmurConnection, MurmurConnection]:
        murmur_connection_1 = MurmurConnection()
        murmur_connection_2 = MurmurConnection()
        return (murmur_connection_1, murmur_connection_2)

    def test_murmur_connection_singleton_without_params(self, murmur_singletons: Tuple[MurmurConnection, MurmurConnection]) -> None:
        murmur_connection_1 = murmur_singletons[0]
        murmur_connection_2 = murmur_singletons[1]
        assert murmur_connection_1 is murmur_connection_2

    def test_murmur_connection_singleton_with_params(
        self, murmur_singletons: Tuple[MurmurConnection, MurmurConnection], valid_connection_params
    ) -> None:
        murmur_connection_1 = murmur_singletons[0]
        murmur_connection_2 = murmur_singletons[1]

        murmur_connection_1._connection_params = valid_connection_params

        assert murmur_connection_1._connection_params == murmur_connection_2._connection_params
