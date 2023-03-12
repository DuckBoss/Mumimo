import pytest

from src.murmur_connection import MurmurConnectionSingleton


class TestMurmurConnectionSingleton:
    @pytest.fixture(autouse=True)
    def murmur_singletons(self):
        murmur_connection_1 = MurmurConnectionSingleton()
        murmur_connection_2 = MurmurConnectionSingleton()
        yield (murmur_connection_1, murmur_connection_2)
        if hasattr(murmur_connection_1, "_instance"):
            murmur_connection_1.clear()

    def test_murmur_connection_singleton_without_params(self, murmur_singletons) -> None:
        murmur_connection_1 = murmur_singletons[0]
        murmur_connection_2 = murmur_singletons[1]
        assert murmur_connection_1 is murmur_connection_2
        assert murmur_connection_1._instance is murmur_connection_2._instance
        assert murmur_connection_1._murmur_connection_instance is murmur_connection_2._murmur_connection_instance

    def test_murmur_connection_singleton_with_params(self, murmur_singletons, valid_connection_params) -> None:
        murmur_connection_1 = murmur_singletons[0]
        murmur_connection_2 = murmur_singletons[1]

        murmur_connection_1.instance()._connection_params = valid_connection_params

        assert murmur_connection_1.instance()._connection_params == murmur_connection_2.instance()._connection_params
