import argparse

from . import version

args_parser = argparse.ArgumentParser(
    prog="Mumimo",
    usage="mumimo ...",
    description="A plugin-based All-In-One mumble bot client solution in python 3.8+ with extensive features and support for custom plugins.",
)
args_parser.add_argument(
    "-version",
    "--version",
    help="displays the application version",
    action="version",
    version=f"Mumimo v{version.version()}",
)

# Connection system arguments
group_connection = args_parser.add_argument_group("connection")
group_connection.add_argument("-sh", "--host", help="host IP of murmur server", type=str)
group_connection.add_argument("-sp", "--port", help="host port of murmur server", type=int)
group_connection.add_argument("-u", "--user", help="the client username", type=str)
group_connection.add_argument("-p", "--password", help="the client password", type=str)
group_connection.add_argument("-c", "--cert-file", help="path to user certificate", type=str)
group_connection.add_argument("-k", "--key-file", help="path to private key associated with user certificate", type=str)
group_connection.add_argument("-t", "--tokens", help="channel access tokens as a list of strings", type=str)
group_connection.add_argument("-ar", "--auto-reconnect", help="attempt to reconnect to the server if disconnected", action="store_true")
group_connection.add_argument("-su", "--superuser", help="the user profile that has full access to this client", type=str)

# Other system arguments
group_other = args_parser.add_argument_group("other")
group_other.add_argument("-cf", "--config-file", help="use a custom config file from the given path", type=str)
group_other.add_argument("-lcf", "--log-config-file", help="use a custom config file for logging from the given path", type=str)
group_other.add_argument("-v", "--verbose", help="enables verbose and debug messages to output to the console", action="count", default=0)
group_other.add_argument(
    "-gc",
    "--generate-cert",
    help="automatically generates a self-signed certificate if none exists",
    action="store_true",
)
group_other.add_argument("-e", "--env-file", help="use connection options from an environment file", type=str)

# Database system arguments
group_database = args_parser.add_argument_group("database")
group_database.add_argument(
    "-dbdi", "--db-dialect", help="specify the database dialect based on the database type (ex: sqlite, postgresql, mysql, etc.)", type=str
)
group_database.add_argument(
    "-dbdr",
    "--db-driver",
    help="specify the database connection driver based on the database type (ex: aiosqlite, pymyssql, pyodbc, pymysql, etc.)",
    type=str,
)
group_database.add_argument("-dbu", "--db-user", help="specify the database connection username", type=str)
group_database.add_argument("-dbp", "--db-pass", help="specify the database connection password", type=str)
group_database.add_argument("-dbh", "--db-host", help="specify the database connection host", type=str)
group_database.add_argument("-dbn", "--db-name", help="specify the database name", type=str)
group_database.add_argument("-dbq", "--db-query", help="specify the database query", type=str)
