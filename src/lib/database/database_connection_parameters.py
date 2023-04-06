from typing import Any, Dict, Optional, Tuple


class DatabaseConnectionParameters:
    def __init__(
        self,
        dialect: str,
        host: str,
        port: Optional[str] = None,
        database_name: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        drivername: Optional[str] = None,
        use_remote: bool = False,
        local_database_dialect: Optional[str] = None,
        local_database_path: Optional[str] = None,
        local_database_driver: Optional[str] = None,
    ) -> None:
        self.drivername = drivername
        self.dialect = dialect
        self.username = username
        self.host = host
        self.port = port
        self.database_name = database_name
        self.password = password
        self.use_remote = use_remote
        self.local_database_dialect = local_database_dialect
        self.local_database_path = local_database_path
        self.local_database_driver = local_database_driver

    def validate_parameters(self) -> Tuple[bool, str]:
        if self.use_remote:
            if self.database_name is None or self.database_name == "":
                return False, f"database_name={self.database_name}"
            if self.username is None or self.username == "":
                return False, f"username={self.username}"
            if self.password is None or self.password == "":
                return False, f"password={self.password}"
            if self.port is None or int(self.port) <= 0:
                return False, f"port={self.port}"
            if self.dialect is None or self.dialect == "":
                return False, f"dialect={self.dialect}"
            if self.drivername is None or self.drivername == "":
                return False, f"drivername={self.drivername}"
            if self.host is None or self.host == "":
                return False, f"host={self.host}"
        else:
            if self.local_database_path is None or self.local_database_path == "":
                return False, f"local_database_path={self.local_database_path}"
            if self.local_database_dialect is None or self.local_database_dialect == "":
                return False, f"local_database_dialect={self.local_database_dialect}"
            if self.local_database_driver is None or self.local_database_driver == "":
                return False, f"local_database_driver={self.local_database_driver}"

        return True, ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dialect": self.dialect,
            "drivername": self.drivername,
            "host": self.host,
            "port": self.port,
            "name": self.database_name,
            "username": self.username,
            "password": self.password,
            "use_remote": self.use_remote,
            "local_database_path": self.local_database_path,
            "local_database_dialect": self.local_database_dialect,
            "local_database_driver": self.local_database_driver,
        }
