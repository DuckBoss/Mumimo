from typing import Any, Dict, Optional, Tuple


class DatabaseConnectionParameters:
    def __init__(
        self,
        dialect: str,
        database: str,
        host: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        drivername: Optional[str] = None,
        query: Optional[str] = None,
    ) -> None:
        self.drivername = drivername
        self.dialect = dialect
        self.username = username
        self.host = host
        self.database = database
        self.password = password
        self.query = query

    def set_drivername(self, drivername: str) -> None:
        self.drivername = drivername.strip()

    def set_dialect(self, dialect: str) -> None:
        self.dialect = dialect.strip()

    def set_username(self, username: str) -> None:
        self.username = username.strip()

    def set_host(self, host: str) -> None:
        self.host = host.strip()

    def set_database(self, database: str) -> None:
        self.database = database.strip()

    def set_password(self, password: str) -> None:
        self.password = password.strip()

    def set_query(self, query: str) -> None:
        self.query = query.strip()

    def validate_parameters(
        self, no_database_name: bool = False, no_credentials: bool = False, no_driver: bool = False, no_query: bool = False
    ) -> Tuple[bool, str]:
        if self.dialect is None or self.dialect == "":
            return False, f"dialect={self.dialect}"
        if self.host is None or self.host == "":
            return False, f"host={self.host}"

        if not no_database_name:
            if self.database is None or self.database == "":
                return False, f"database={self.database}"
        if not no_driver:
            if self.drivername is None or self.drivername == "":
                return False, f"drivername={self.drivername}"
        if not no_query:
            if self.query is None or self.query == "":
                return False, f"query={self.query}"

        if not no_credentials:
            if self.username is None or self.username == "":
                return False, f"username={self.username}"
            if self.password is not None or self.password == "":
                return False, f"password={self.password}"
        return True, ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dialect": self.dialect,
            "drivername": self.drivername,
            "host": self.host,
            "database": self.database,
            "username": self.username,
            "password": self.password,
            "query": self.query,
        }
