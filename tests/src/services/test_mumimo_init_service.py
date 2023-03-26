from typing import Any, Dict
from unittest.mock import patch

import pytest

from src.config import Config
from src.services.init_services.mumimo_init_service import MumimoInitService


class TestMumimoInitService:
    @pytest.fixture(autouse=True)
    def get_service(self):
        return MumimoInitService({})

    @pytest.fixture(autouse=True)
    def get_config(self):
        return Config("tests/data/config/test_config.toml")

    def test_init(self, get_service) -> None:
        init_service: MumimoInitService = get_service
        assert init_service._sys_args == {}
        assert init_service._cfg_init_service is not None
        assert init_service._client_settings_init_service is not None

    @pytest.mark.asyncio
    @patch("src.services.init_services.client_settings_init_service.ClientSettingsInitService.get_prioritized_env_options")
    @patch("src.services.database_service.DatabaseService.initialize_database")
    @patch("src.services.init_services.client_settings_init_service.ClientSettingsInitService.initialize_client_settings")
    @patch("src.services.init_services.cfg_init_service.ConfigInitService.initialize_config")
    async def test_initialize(
        self,
        mock_init_cfg,
        mock_init_settings,
        mock_db_init,
        mock_prioritized_env,
        get_config: Dict[str, Any],
        get_service: MumimoInitService,
    ) -> None:
        init_service: MumimoInitService = get_service
        init_service._sys_args = {}

        mock_init_cfg.return_value = get_config
        mock_init_settings.return_value = None
        mock_prioritized_env.return_value = {}
        mock_db_init.return_value = None

        await init_service.initialize()

        mock_init_cfg.assert_called_once()
        mock_init_settings.assert_called_once()
        mock_prioritized_env.assert_called_once()
        mock_db_init.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.services.init_services.client_settings_init_service.ClientSettingsInitService.get_connection_parameters")
    async def test_get_connection_parameters_prioritized_options_are_none(self, mock_conn_params, get_service: MumimoInitService) -> None:
        mock_conn_params.return_value = {"test": "test"}
        init_service: MumimoInitService = get_service
        assert await init_service.get_connection_parameters() == {"test": "test"}
