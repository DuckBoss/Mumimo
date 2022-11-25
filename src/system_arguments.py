import argparse

import version as vz

args_parser = argparse.ArgumentParser()
args_parser.add_argument(
    "-v",
    "--version",
    help="displays the application version",
    action="version",
    version=f"Mumimo v{vz.VERSION}",
)
args_parser.add_argument("-hl", "--headless", help="runs the application with no console output", action="store_true")
args_parser.add_argument("-sh", "--host", help="host IP of mumble server", type=str)
args_parser.add_argument("-sp", "--port", help="host port of mumble server", type=int)
args_parser.add_argument("-c", "--cert", help="path to user certificate", type=str)
args_parser.add_argument("-super", "--superuser", help="the user profile that has full access to this client", type=str)
args_parser.add_argument(
    "-gc",
    "--generate-cert",
    help="automatically generates a self-signed certificate if none exists",
    action="store_true",
)
args_parser.add_argument("-e", "--env-file", help="use configuration options from an environment file", type=str)
