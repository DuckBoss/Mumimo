from typing import Any, Tuple

import pytest

from src.lib.database.database_connection_parameters import DatabaseConnectionParameters


class TestDatabaseConnectionParameters:
    @pytest.fixture(autouse=True)
    def get_connection_params(self) -> Tuple[Any, ...]:
        return (
            "mumimo_dialect",  # dialect
            "mumimo_host.db",  # host
            "mumimo_port",  # port
            "mumimo_database_name",  # database
            "mumimo_user",  # username
            "mumimo_pass",  # password
            "mumimo_drivername",  # drivername
            False,  # use remote
            "mumimo_localdb_dialect",  # local db dialect
            "mumimo_localdb_path.db",  # local db path
            "mumimo_localdb_drivername",  # local db drivername
        )

    @pytest.fixture(autouse=True)
    def get_params_object(self, get_connection_params: Tuple[str, ...]) -> DatabaseConnectionParameters:
        _params: DatabaseConnectionParameters = DatabaseConnectionParameters(*get_connection_params)  # type: ignore
        return _params

    def test_init_database_connection_parameters(self, get_connection_params: Tuple[str, ...]) -> None:
        _params: DatabaseConnectionParameters = DatabaseConnectionParameters(*get_connection_params)  # type: ignore
        assert _params.dialect == get_connection_params[0]
        assert _params.host == get_connection_params[1]
        assert _params.port == get_connection_params[2]
        assert _params.database_name == get_connection_params[3]
        assert _params.username == get_connection_params[4]
        assert _params.password == get_connection_params[5]
        assert _params.drivername == get_connection_params[6]
        assert _params.use_remote == get_connection_params[7]
        assert _params.local_database_dialect == get_connection_params[8]
        assert _params.local_database_path == get_connection_params[9]
        assert _params.local_database_driver == get_connection_params[10]

    def test_to_dict(self, get_params_object: DatabaseConnectionParameters) -> None:
        _params: DatabaseConnectionParameters = get_params_object
        assert _params.to_dict() == {
            "dialect": _params.dialect,
            "drivername": _params.drivername,
            "host": _params.host,
            "port": _params.port,
            "database_name": _params.database_name,
            "username": _params.username,
            "password": _params.password,
            "use_remote": _params.use_remote,
            "local_database_path": _params.local_database_path,
            "local_database_dialect": _params.local_database_dialect,
            "local_database_driver": _params.local_database_driver,
        }

    class TestValidateParameters:
        @pytest.fixture(autouse=True)
        def get_params(self, get_params_object: DatabaseConnectionParameters) -> DatabaseConnectionParameters:
            _params: DatabaseConnectionParameters = get_params_object
            _params.database_name = "test"
            _params.dialect = "test"
            _params.host = "test"
            _params.port = "12345"
            _params.username = "test"
            _params.password = "test"
            _params.drivername = "test"
            _params.local_database_dialect = "test"
            _params.local_database_driver = "test"
            _params.local_database_path = "test"
            _params.use_remote = False
            return _params

        def test_validate_parameters_default(self, get_params_object: DatabaseConnectionParameters) -> None:
            _params: DatabaseConnectionParameters = get_params_object
            _params.use_remote = False
            assert _params.validate_parameters() == (True, "")
            _params.use_remote = True
            assert _params.validate_parameters() == (True, "")

        class TestRemote:
            remote_vars = ["database_name", "username", "password", "port", "dialect", "drivername", "host"]

            @pytest.mark.parametrize("name", remote_vars)
            def test_validate_parameters_remote_invalid_parameters(self, name: str, get_params: DatabaseConnectionParameters) -> None:
                _params: DatabaseConnectionParameters = get_params
                _params.use_remote = True

                print(_params.to_dict(), name)
                setattr(_params, name, None)
                assert _params.validate_parameters() == (False, f"{name}=None")
                setattr(_params, name, "")
                assert _params.validate_parameters() == (False, f"{name}=")

        class TestLocal:
            local_vars = ["local_database_path", "local_database_dialect", "local_database_driver"]

            @pytest.mark.parametrize("name", local_vars)
            def test_validate_parameters_local_invalid_parameters(self, name: str, get_params: DatabaseConnectionParameters) -> None:
                _params: DatabaseConnectionParameters = get_params
                _params.use_remote = False

                setattr(_params, name, None)
                assert _params.validate_parameters() == (False, f"{name}=None")
                setattr(_params, name, "")
                assert _params.validate_parameters() == (False, f"{name}=")
