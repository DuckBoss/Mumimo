import argparse

from . import version

args_parser = argparse.ArgumentParser()
args_parser.add_argument(
    "-version",
    "--version",
    help="displays the application version",
    action="version",
    version=f"Mumimo v{version.version()}",
)
args_parser.add_argument("-hl", "--headless", help="runs the application with no console output", action="store_true")
args_parser.add_argument("-cf", "--config-file", help="use a custom config file from the given path", type=str)
args_parser.add_argument("-lcf", "--log-config-file", help="use a custom config file for logging from the given path", type=str)
args_parser.add_argument("-sh", "--host", help="host IP of murmur server", type=str)
args_parser.add_argument("-sp", "--port", help="host port of murmur server", type=int)
args_parser.add_argument("-u", "--user", help="the client username", type=str)
args_parser.add_argument("-p", "--password", help="the client password", type=str)
args_parser.add_argument("-c", "--cert-file", help="path to user certificate", type=str)
args_parser.add_argument("-k", "--key-file", help="path to private key associated with user certificate", type=str)
args_parser.add_argument("-t", "--tokens", help="channel access tokens as a list of strings", type=str)
args_parser.add_argument("-ar", "--auto-reconnect", help="attempt to reconnect to the server if disconnected", action="store_true")
args_parser.add_argument("-v", "--verbose", help="enables verbose and debug messages to output to the console", action="count", default=0)
args_parser.add_argument("-su", "--superuser", help="the user profile that has full access to this client", type=str)
args_parser.add_argument(
    "-gc",
    "--generate-cert",
    help="automatically generates a self-signed certificate if none exists",
    action="store_true",
)
args_parser.add_argument("-e", "--env-file", help="use connection options from an environment file", type=str)
