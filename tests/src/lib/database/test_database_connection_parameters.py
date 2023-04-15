from typing import Tuple, Any

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
        _params: DatabaseConnectionParameters = DatabaseConnectionParameters(*get_connection_params)
        return _params

    def test_init_database_connection_parameters(self, get_connection_params: Tuple[str, ...]) -> None:
        _params: DatabaseConnectionParameters = DatabaseConnectionParameters(*get_connection_params)
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
            "database": _params.database_name,
            "username": _params.username,
            "password": _params.password,
            "use_remote": _params.use_remote,
            "local_database_path": _params.local_database_path,
            "local_database_dialect": _params.local_database_dialect,
            "local_database_driver": _params.local_database_driver,
        }

    class TestValidateParameters:
        def test_validate_parameters_default(self, get_params_object: DatabaseConnectionParameters) -> None:
            _params: DatabaseConnectionParameters = get_params_object
            assert _params.validate_parameters() == (True, "")

        # TODO: Test cases of individual connection parameters...
