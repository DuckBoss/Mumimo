import argparse

from . import version

args_parser = argparse.ArgumentParser()
args_parser.add_argument(
    "-v",
    "--version",
    help="displays the application version",
    action="version",
    version=f"Mumimo v{version.VERSION}",
)
args_parser.add_argument("-hl", "--headless", help="runs the application with no console output", action="store_true")
args_parser.add_argument("-sh", "--host", help="host IP of murmur server", type=str)
args_parser.add_argument("-sp", "--port", help="host port of murmur server", type=int)
args_parser.add_argument("-u", "--user", help="the client username", type=str)
args_parser.add_argument("-p", "--password", help="the client password", type=str)
args_parser.add_argument("-c", "--certfile", help="path to user certificate", type=str)
args_parser.add_argument("-k", "--keyfile", help="path to private key associated with user certificate", type=str)
args_parser.add_argument("-r", "--reconnect", help="attempt to reconnect to the server if disconnected", action="store_true")
args_parser.add_argument("-t", "--tokens", help="channel access tokens as a list of strings", type=str)
args_parser.add_argument("-d", "--debug", help="enables debug messages to output to the console", action="store_true")
args_parser.add_argument("-super", "--superuser", help="the user profile that has full access to this client", type=str)
args_parser.add_argument(
    "-gc",
    "--generate-cert",
    help="automatically generates a self-signed certificate if none exists",
    action="store_true",
)
args_parser.add_argument("-e", "--env-file", help="use connection options from an environment file", type=str)
