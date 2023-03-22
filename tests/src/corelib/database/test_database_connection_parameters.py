from typing import Tuple

import pytest

from src.corelib.database.database_connection_parameters import DatabaseConnectionParameters


class TestDatabaseConnectionParameters:
    @pytest.fixture(autouse=True)
    def get_connection_params(self) -> Tuple[str, ...]:
        return (
            "mumimo_dialect",  # dialect
            "mumimo_host.db",  # host
            "mumimo_database",  # database
            "mumimo_user",  # username
            "mumimo_pass",  # password
            "mumimo_drivername",  # drivername
            "mumimo_query",  # query
        )

    @pytest.fixture(autouse=True)
    def get_params_object(self, get_connection_params: Tuple[str, ...]) -> DatabaseConnectionParameters:
        _params: DatabaseConnectionParameters = DatabaseConnectionParameters(*get_connection_params)
        return _params

    def test_init_database_connection_parameters(self, get_connection_params: Tuple[str, ...]) -> None:
        _params: DatabaseConnectionParameters = DatabaseConnectionParameters(*get_connection_params)
        assert _params.dialect == get_connection_params[0]
        assert _params.host == get_connection_params[1]
        assert _params.database == get_connection_params[2]
        assert _params.username == get_connection_params[3]
        assert _params.password == get_connection_params[4]
        assert _params.drivername == get_connection_params[5]
        assert _params.query == get_connection_params[6]

    def test_to_dict(self, get_params_object: DatabaseConnectionParameters) -> None:
        _params: DatabaseConnectionParameters = get_params_object
        assert _params.to_dict() == {
            "dialect": _params.dialect,
            "drivername": _params.drivername,
            "host": _params.host,
            "database": _params.database,
            "username": _params.username,
            "password": _params.password,
            "query": _params.query,
        }

    class TestValidateParameters:
        def test_validate_parameters_default(self, get_params_object: DatabaseConnectionParameters) -> None:
            _params: DatabaseConnectionParameters = get_params_object
            assert _params.validate_parameters() == (True, "")

        def test_validate_parameters_dialect(self, get_params_object: DatabaseConnectionParameters) -> None:
            _params: DatabaseConnectionParameters = get_params_object
            _params.dialect = ""
            assert _params.validate_parameters() == (False, f"dialect={_params.dialect}")
            _params.dialect = None  # type: ignore
            assert _params.validate_parameters() == (False, f"dialect={_params.dialect}")

        def test_validate_parameters_host(self, get_params_object: DatabaseConnectionParameters) -> None:
            _params: DatabaseConnectionParameters = get_params_object
            _params.host = ""
            assert _params.validate_parameters() == (False, f"host={_params.host}")
            _params.host = None  # type: ignore
            assert _params.validate_parameters() == (False, f"host={_params.host}")

        def test_validate_parameters_database(self, get_params_object: DatabaseConnectionParameters) -> None:
            _params: DatabaseConnectionParameters = get_params_object
            _params.database = ""
            assert _params.validate_parameters(no_database_name=False) == (False, f"database={_params.database}")
            _params.database = None  # type: ignore
            assert _params.validate_parameters(no_database_name=False) == (False, f"database={_params.database}")

            _params.database = ""
            assert _params.validate_parameters(no_database_name=True) == (True, "")
            _params.database = None  # type: ignore
            assert _params.validate_parameters(no_database_name=True) == (True, "")

        def test_validate_parameters_drivername(self, get_params_object: DatabaseConnectionParameters) -> None:
            _params: DatabaseConnectionParameters = get_params_object
            _params.drivername = ""
            assert _params.validate_parameters(no_driver=False) == (False, f"drivername={_params.drivername}")
            _params.drivername = None  # type: ignore
            assert _params.validate_parameters(no_driver=False) == (False, f"drivername={_params.drivername}")

            _params.drivername = ""
            assert _params.validate_parameters(no_driver=True) == (True, "")
            _params.drivername = None  # type: ignore
            assert _params.validate_parameters(no_driver=True) == (True, "")

        def test_validate_parameters_query(self, get_params_object: DatabaseConnectionParameters) -> None:
            _params: DatabaseConnectionParameters = get_params_object
            _params.query = ""
            assert _params.validate_parameters(no_query=False) == (False, f"query={_params.query}")
            _params.query = None  # type: ignore
            assert _params.validate_parameters(no_query=False) == (False, f"query={_params.query}")

            _params.query = ""
            assert _params.validate_parameters(no_query=True) == (True, "")
            _params.query = None  # type: ignore
            assert _params.validate_parameters(no_query=True) == (True, "")

        def test_validate_parameters_username(self, get_params_object: DatabaseConnectionParameters) -> None:
            _params: DatabaseConnectionParameters = get_params_object
            _params.username = ""
            assert _params.validate_parameters(no_credentials=False) == (False, f"username={_params.username}")
            _params.username = None  # type: ignore
            assert _params.validate_parameters(no_credentials=False) == (False, f"username={_params.username}")

            _params.username = ""
            assert _params.validate_parameters(no_credentials=True) == (True, "")
            _params.username = None  # type: ignore
            assert _params.validate_parameters(no_credentials=True) == (True, "")

        def test_validate_parameters_password(self, get_params_object: DatabaseConnectionParameters) -> None:
            _params: DatabaseConnectionParameters = get_params_object
            _params.password = ""
            assert _params.validate_parameters(no_credentials=False) == (False, f"password={_params.password}")
            _params.password = None  # type: ignore
            assert _params.validate_parameters(no_credentials=False) == (False, f"password={_params.password}")

            _params.password = ""
            assert _params.validate_parameters(no_credentials=True) == (True, "")
            _params.password = None  # type: ignore
            assert _params.validate_parameters(no_credentials=True) == (True, "")

    class TestSets:
        def test_set_drivername(self, get_params_object: DatabaseConnectionParameters) -> None:
            _params: DatabaseConnectionParameters = get_params_object
            assert _params.drivername == "mumimo_drivername"
            _params.set_drivername("test_drivername")
            assert _params.drivername == "test_drivername"

        def test_set_dialect(self, get_params_object: DatabaseConnectionParameters) -> None:
            _params: DatabaseConnectionParameters = get_params_object
            assert _params.dialect == "mumimo_dialect"
            _params.set_dialect("test_dialect")
            assert _params.dialect == "test_dialect"

        def test_set_username(self, get_params_object: DatabaseConnectionParameters) -> None:
            _params: DatabaseConnectionParameters = get_params_object
            assert _params.username == "mumimo_user"
            _params.set_username("test_username")
            assert _params.username == "test_username"

        def test_set_host(self, get_params_object: DatabaseConnectionParameters) -> None:
            _params: DatabaseConnectionParameters = get_params_object
            assert _params.host == "mumimo_host.db"
            _params.set_host("test_host.db")
            assert _params.host == "test_host.db"

        def test_set_database(self, get_params_object: DatabaseConnectionParameters) -> None:
            _params: DatabaseConnectionParameters = get_params_object
            assert _params.database == "mumimo_database"
            _params.set_database("test_database")
            assert _params.database == "test_database"

        def test_set_password(self, get_params_object: DatabaseConnectionParameters) -> None:
            _params: DatabaseConnectionParameters = get_params_object
            assert _params.password == "mumimo_pass"
            _params.set_password("test_password")
            assert _params.password == "test_password"

        def test_set_query(self, get_params_object: DatabaseConnectionParameters) -> None:
            _params: DatabaseConnectionParameters = get_params_object
            assert _params.query == "mumimo_query"
            _params.set_query("test_query")
            assert _params.query == "test_query"
