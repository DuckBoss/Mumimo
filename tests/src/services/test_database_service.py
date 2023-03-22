import asyncio
from typing import Dict, Tuple
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, async_sessionmaker

from src.corelib.database.database_connection_parameters import DatabaseConnectionParameters
from src.exceptions import DatabaseServiceError
from src.services.database_service import DatabaseService


class TestDatabaseService:
    @pytest.fixture(autouse=True)
    def get_connection_params(self) -> Dict[str, str]:
        return {
            "dialect": "sqlite",  # dialect
            "database": "mumimo",  # database
            "host": "/tmp/mumimo_test.db",  # host
            "drivername": "aiosqlite",  # drivername
        }

    @pytest.fixture(autouse=True)
    def get_connection_params_object(self, get_connection_params: Dict[str, str]) -> DatabaseConnectionParameters:
        return DatabaseConnectionParameters(
            dialect=get_connection_params["dialect"],
            database=get_connection_params["database"],
            host=get_connection_params["host"],
            drivername=get_connection_params["drivername"],
        )

    @pytest.mark.asyncio
    @pytest.fixture(autouse=True)
    @patch.object(DatabaseService, "import_default_values")
    @patch.object(DatabaseService, "setup")
    async def get_database_service(self, mock_setup, mock_import, get_connection_params: Dict[str, str]) -> DatabaseService:
        mock_setup.return_value = None
        mock_import.return_value = None
        _dialect: str = get_connection_params["dialect"]
        _database: str = get_connection_params["database"]
        _host: str = get_connection_params["host"]
        _drivername: str = get_connection_params["drivername"]
        _db_service: DatabaseService = DatabaseService()
        await _db_service.initialize_database(dialect=_dialect, database=_database, host=_host, drivername=_drivername)
        return _db_service

    class TestInit:
        @pytest.mark.asyncio
        @patch.object(DatabaseService, "import_default_values")
        @patch.object(DatabaseService, "setup")
        async def test_initialize_database(self, mock_setup: "MagicMock", mock_import: "MagicMock", get_connection_params: Dict[str, str]) -> None:
            mock_setup.return_value = None
            mock_import.return_value = None
            _dialect: str = get_connection_params["dialect"]
            _database: str = get_connection_params["database"]
            _host: str = get_connection_params["host"]
            _drivername: str = get_connection_params["drivername"]
            _db_service: DatabaseService = DatabaseService()
            await _db_service.initialize_database(dialect=_dialect, database=_database, host=_host, drivername=_drivername)
            mock_setup.assert_called_once()
            mock_import.assert_called_once()

    class TestValidateParameters:
        @pytest.mark.asyncio
        async def test_validate_no_checks(
            self, get_connection_params_object: DatabaseConnectionParameters, get_database_service: DatabaseService
        ) -> None:
            _params: DatabaseConnectionParameters = get_connection_params_object
            _db_service: DatabaseService = get_database_service
            _params.query = "test"
            _params.username = "test"
            _params.password = "test"
            _params.database = "test"
            _params.dialect = "test"
            _params.drivername = "test"

            result: Tuple[bool, str] = await _db_service._validate_connection_parameters(_params)
            assert result == (True, "")

        @pytest.mark.asyncio
        @patch.object(DatabaseConnectionParameters, "validate_parameters")
        async def test_validate_check_credentials(
            self, mock_validate, get_connection_params_object: DatabaseConnectionParameters, get_database_service: DatabaseService
        ) -> None:
            _params: DatabaseConnectionParameters = get_connection_params_object
            _db_service: DatabaseService = get_database_service
            _params.query = "test"

            _params.username = "test"
            _params.password = None
            await _db_service._validate_connection_parameters(_params)
            mock_validate.assert_called_with(
                no_database_name=False,
                no_credentials=True,
                no_driver=False,
                no_query=False,
            )
            _params.username = None
            _params.password = "test"
            await _db_service._validate_connection_parameters(_params)
            mock_validate.assert_called_with(
                no_database_name=False,
                no_credentials=True,
                no_driver=False,
                no_query=False,
            )

        @pytest.mark.asyncio
        @patch.object(DatabaseConnectionParameters, "validate_parameters")
        async def test_validate_check_drivername(
            self, mock_validate, get_connection_params_object: DatabaseConnectionParameters, get_database_service: DatabaseService
        ) -> None:
            _params: DatabaseConnectionParameters = get_connection_params_object
            _db_service: DatabaseService = get_database_service
            _params.query = "test"
            _params.username = "test"
            _params.password = "test"

            _params.drivername = None
            await _db_service._validate_connection_parameters(_params)
            mock_validate.assert_called_with(
                no_database_name=False,
                no_credentials=False,
                no_driver=True,
                no_query=False,
            )

            _params.drivername = "test"
            await _db_service._validate_connection_parameters(_params)
            mock_validate.assert_called_with(
                no_database_name=False,
                no_credentials=False,
                no_driver=False,
                no_query=False,
            )

        @pytest.mark.asyncio
        @patch.object(DatabaseConnectionParameters, "validate_parameters")
        async def test_validate_check_query(
            self, mock_validate, get_connection_params_object: DatabaseConnectionParameters, get_database_service: DatabaseService
        ) -> None:
            _params: DatabaseConnectionParameters = get_connection_params_object
            _db_service: DatabaseService = get_database_service
            _params.username = "test"
            _params.password = "test"

            _params.query = None
            await _db_service._validate_connection_parameters(_params)
            mock_validate.assert_called_with(
                no_database_name=False,
                no_credentials=False,
                no_driver=False,
                no_query=True,
            )

            _params.query = "test"
            await _db_service._validate_connection_parameters(_params)
            mock_validate.assert_called_with(
                no_database_name=False,
                no_credentials=False,
                no_driver=False,
                no_query=False,
            )

        @pytest.mark.asyncio
        @patch.object(DatabaseConnectionParameters, "validate_parameters")
        async def test_validate_check_database_name(
            self, mock_validate, get_connection_params_object: DatabaseConnectionParameters, get_database_service: DatabaseService
        ) -> None:
            _params: DatabaseConnectionParameters = get_connection_params_object
            _db_service: DatabaseService = get_database_service
            _params.username = "test"
            _params.password = "test"
            _params.query = "test"

            _params.database = None  # type: ignore
            await _db_service._validate_connection_parameters(_params)
            mock_validate.assert_called_with(
                no_database_name=True,
                no_credentials=False,
                no_driver=False,
                no_query=False,
            )

            _params.database = "test"
            await _db_service._validate_connection_parameters(_params)
            mock_validate.assert_called_with(
                no_database_name=False,
                no_credentials=False,
                no_driver=False,
                no_query=False,
            )

    class TestSession:
        @pytest.mark.asyncio
        async def test_get_session_no_session_factory(self, get_database_service: DatabaseService) -> None:
            _db_service: DatabaseService = get_database_service
            _db_service._session_factory = None
            with pytest.raises(DatabaseServiceError, match=r"an uninitialized session factory.$"):
                async with _db_service.session() as _:
                    pass

        @pytest.mark.asyncio
        async def test_get_session_exception_raised(self, get_database_service: DatabaseService) -> None:
            _db_service: DatabaseService = get_database_service
            _db_service._session_factory = async_scoped_session(
                session_factory=async_sessionmaker(_db_service._engine, class_=AsyncSession, expire_on_commit=False),
                scopefunc=asyncio.current_task,
            )
            with pytest.raises(DatabaseServiceError, match=r"Rolled back changes.$"):
                async with _db_service.session() as _:
                    raise Exception("something went wrong with getting a session")

        @pytest.mark.asyncio
        async def test_get_session(self, get_database_service: DatabaseService) -> None:
            _db_service: DatabaseService = get_database_service
            _db_service._session_factory = async_scoped_session(
                session_factory=async_sessionmaker(_db_service._engine, class_=AsyncSession, expire_on_commit=False),
                scopefunc=asyncio.current_task,
            )
            async with _db_service.session() as session:
                assert isinstance(session, AsyncSession) is True

    class TestClose:
        @pytest.mark.asyncio
        @patch("sqlalchemy.ext.asyncio.AsyncEngine.dispose")
        async def test_close_no_engine(self, mock_dispose, get_database_service: DatabaseService) -> None:
            _db_service: DatabaseService = get_database_service
            _db_service._engine = None
            await _db_service.close()
            assert _db_service._engine is None
            assert not mock_dispose.called

        @pytest.mark.asyncio
        async def test_close_no_clean(self, get_database_service: DatabaseService) -> None:
            _db_service: DatabaseService = get_database_service
            _db_service._engine = AsyncMock()
            _db_service._connection_parameters = AsyncMock()
            _db_service._session_factory = AsyncMock()
            await _db_service.close(clean=False)
            assert _db_service._connection_parameters is not None
            assert _db_service._session_factory is not None
            assert _db_service._engine is not None

        @pytest.mark.asyncio
        async def test_close_clean(self, get_database_service: DatabaseService) -> None:
            _db_service: DatabaseService = get_database_service
            _db_service._engine = AsyncMock()
            _db_service._connection_parameters = AsyncMock()
            _db_service._session_factory = AsyncMock()
            await _db_service.close(clean=True)
            assert _db_service._connection_parameters is None
            assert _db_service._session_factory is None
            assert _db_service._engine is None

    class TestSetup:
        @pytest.mark.asyncio
        async def test_setup_engine_exists(
            self, get_connection_params_object: DatabaseConnectionParameters, get_database_service: DatabaseService
        ) -> None:
            _db_connection_params: DatabaseConnectionParameters = get_connection_params_object
            _db_service: DatabaseService = get_database_service
            _db_service._engine = MagicMock()
            with pytest.raises(DatabaseServiceError, match=r"Close the connection first.$"):
                _ = await _db_service.setup(_db_connection_params)

        @pytest.mark.asyncio
        async def test_setup_connection_parameters_is_none(self, get_database_service: DatabaseService) -> None:
            _db_connection_params = None
            _db_service: DatabaseService = get_database_service
            _db_service._engine = None
            with pytest.raises(DatabaseServiceError, match=r"Connection parameters were not provided.$"):
                _ = await _db_service.setup(_db_connection_params)  # type: ignore

        @pytest.mark.asyncio
        async def test_setup_connection_parameters_fails_validation(
            self, get_connection_params_object: DatabaseConnectionParameters, get_database_service: DatabaseService
        ) -> None:
            _db_connection_params: DatabaseConnectionParameters = get_connection_params_object
            _db_connection_params.dialect = None  # type: ignore

            _db_service: DatabaseService = get_database_service
            _db_service._engine = None
            with pytest.raises(DatabaseServiceError, match=r"Connection parameters are invalid - 'dialect=None'.$"):
                _ = await _db_service.setup(_db_connection_params)

        @pytest.mark.asyncio
        @patch("src.utils.parsers.db_url_parser.get_url")
        async def test_setup_database_connection_fails_to_open(
            self, mock_get_url, get_connection_params_object: DatabaseConnectionParameters, get_database_service: DatabaseService
        ) -> None:
            _db_connection_params: DatabaseConnectionParameters = get_connection_params_object
            _db_service: DatabaseService = get_database_service
            _db_service._engine = None
            mock_get_url.return_value = ""
            with pytest.raises(DatabaseServiceError, match=r"Please check your connection parameters.$"):
                _ = await _db_service.setup(_db_connection_params)

        @pytest.mark.asyncio
        @patch.object(DatabaseService, "_validate_connection_parameters")
        @patch("src.utils.parsers.db_url_parser.get_url")
        async def test_setup_database_connection_fails_to_open_bad_dialect(
            self, mock_get_url, mock_validate, get_connection_params_object: DatabaseConnectionParameters, get_database_service: DatabaseService
        ) -> None:
            mock_validate.return_value = (True, "")
            _db_connection_params: DatabaseConnectionParameters = get_connection_params_object
            _db_connection_params.dialect = "invalid_dialect"
            _db_service: DatabaseService = get_database_service
            _db_service._engine = None
            mock_get_url.return_value = ""
            with pytest.raises(DatabaseServiceError, match=r"Please check your dialect connection parameters.$"):
                _ = await _db_service.setup(_db_connection_params)

    class TestImportDefaultValues:
        @pytest.mark.asyncio
        async def test_import_engine_is_none(self, get_database_service: DatabaseService) -> None:
            _db_service: DatabaseService = get_database_service
            _db_service._engine = None
            with pytest.raises(DatabaseServiceError, match=r"Database connection engine is not initialized.$"):
                await _db_service.import_default_values()

        @pytest.mark.asyncio
        @patch("src.settings.MumimoSettings.get_mumimo_config")
        async def test_import_config_is_none(self, mock_cfg, get_database_service: DatabaseService) -> None:
            _db_service: DatabaseService = get_database_service
            _db_service._engine = AsyncMock()
            mock_cfg.return_value = None
            with pytest.raises(DatabaseServiceError, match=r"The mumimo config has not been initialized.$"):
                await _db_service.import_default_values()

        @pytest.mark.asyncio
        @patch.object(DatabaseService, "_import_default_aliases")
        @patch.object(DatabaseService, "_import_default_permission_groups")
        @patch("src.settings.MumimoSettings.get_mumimo_config")
        async def test_import_success(self, mock_cfg, mock_import_permissions, mock_import_aliases, get_database_service: DatabaseService) -> None:
            _db_service: DatabaseService = get_database_service
            _db_service._engine = AsyncMock()
            mock_cfg.return_value = AsyncMock()
            mock_import_permissions.return_value = None
            mock_import_aliases.return_value = None
            await _db_service.import_default_values()

    class TestImportDefaultPermissionGroups:
        pass

    class TestImportDefaultAliases:
        pass
