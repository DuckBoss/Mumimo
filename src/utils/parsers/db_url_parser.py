from sqlalchemy.engine.url import URL

from ...lib.database.database_connection_parameters import DatabaseConnectionParameters


def get_url(connection_params: DatabaseConnectionParameters, create_url: bool = False) -> str:
    _port = None
    _host = None
    _user = None
    if create_url:
        if connection_params.local_database_dialect is None:
            connection_params.local_database_dialect = "sqlite"  # Set a default dialect if none is set.
        _drivername = connection_params.local_database_dialect
        _database = connection_params.local_database_path
    else:
        if connection_params.use_remote:
            _drivername = f"{connection_params.dialect}+{connection_params.drivername}"
            _database = connection_params.database_name
            _user = connection_params.username
            _host = connection_params.host
            if connection_params.port is not None:
                _port = int(connection_params.port)
        else:
            if connection_params.local_database_dialect is None:
                connection_params.local_database_dialect = "sqlite"  # Set a default dialect if none is set.
            if connection_params.local_database_driver is None:
                connection_params.local_database_driver = "aiosqlite"  # Set a default database driver if none is set.
            _drivername = f"{connection_params.local_database_dialect}+{connection_params.local_database_driver}"
            _database = connection_params.local_database_path

    url = URL.create(
        drivername=_drivername,
        username=_user,
        password=connection_params.password,
        host=_host,
        port=_port,
        database=_database,
    )
    return url.render_as_string(hide_password=False)
