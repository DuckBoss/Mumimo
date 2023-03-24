import pathlib

from sqlalchemy.engine.url import URL

from ...lib.database.database_connection_parameters import DatabaseConnectionParameters


def get_url(connection_params: DatabaseConnectionParameters, use_driver: bool = True, use_database: bool = True) -> str:
    _drivername = connection_params.dialect
    if connection_params.drivername is not None and use_driver:
        _drivername = f"{_drivername}+{connection_params.drivername}"
    _database = connection_params.database
    if not use_database:
        _database = None
    _host = None
    if connection_params.host is not None:
        _host = "/" + str((pathlib.Path.cwd() / connection_params.host).resolve())

    url = URL.create(
        drivername=_drivername,
        username=connection_params.username,
        host=_host,
        database=_database,
        password=connection_params.password,
    )
    if connection_params.query:
        url.update_query_string(connection_params.query)
    return url.render_as_string(hide_password=False)
