import pytest

from src.config import ConfigSingleton


class TestConfigSingleton:
    @pytest.fixture(autouse=True)
    def config_singletons(self):
        config_1 = ConfigSingleton()
        config_2 = ConfigSingleton()
        yield (config_1, config_2)
        if hasattr(config_1, "_instance"):
            config_1.clear()

    def test_config_singleton_without_params(self, config_singletons) -> None:
        config_1 = config_singletons[0]
        config_2 = config_singletons[1]
        assert config_1 is config_2
        assert config_1._instance is config_2._instance
        assert config_1._config_instance is config_2._config_instance

    def test_config_singleton_with_params(self, config_singletons, valid_config_params) -> None:
        config_1 = config_singletons[0]
        config_2 = config_singletons[1]

        config_1.instance().update(valid_config_params)

        assert config_1.instance() == config_2.instance()
