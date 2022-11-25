from typing import Dict, Optional, Union

from src import murmur_connection
from src.constants import (
    ENV_CERT,
    ENV_HOST,
    ENV_KEY,
    ENV_PASS,
    ENV_PORT,
    ENV_TOKENS,
    ENV_USER,
    SYS_CERT,
    SYS_DEBUG,
    SYS_ENV_FILE,
    SYS_HOST,
    SYS_KEY,
    SYS_PASS,
    SYS_PORT,
    SYS_RECONNECT,
    SYS_TOKENS,
    SYS_USER,
)
from src.system_arguments import args_parser
from src.utils import env_parser


class MumimoService:
    _connection_instance: murmur_connection.MurmurConnection
    _connection_params: Dict[str, Union[Optional[str], Optional[bool]]]

    def __init__(self, sys_args: Dict[str, str]):
        print(sys_args)
        self.interpret_sys_args(sys_args)
        self.initialize_connection(self._connection_params)

    def interpret_sys_args(self, sys_args: Dict[str, str]):
        # Load in options from .env file if present.
        available_env_file: Optional[str] = sys_args.get(SYS_ENV_FILE)
        env_file_dict: Dict[str, Optional[str]] = {}
        if available_env_file is not None:
            env_file_dict = env_parser.read_env_file(available_env_file)
            print(env_file_dict.items())

        # Load in remaining options from system arguments, and prioritize system args
        self._connection_params = {
            SYS_HOST: sys_args.get(SYS_HOST) or env_file_dict.get(ENV_HOST),
            SYS_PORT: sys_args.get(SYS_PORT) or env_file_dict.get(ENV_PORT),
            SYS_USER: sys_args.get(SYS_USER) or env_file_dict.get(ENV_USER),
            SYS_PASS: sys_args.get(SYS_PASS) or env_file_dict.get(ENV_PASS),
            SYS_CERT: sys_args.get(SYS_CERT) or env_file_dict.get(ENV_CERT),
            SYS_KEY: sys_args.get(SYS_KEY) or env_file_dict.get(ENV_KEY),
            SYS_TOKENS: sys_args.get(SYS_TOKENS) or env_file_dict.get(ENV_TOKENS),
            SYS_RECONNECT: bool(sys_args.get(SYS_RECONNECT, False)),
            SYS_DEBUG: bool(sys_args.get(SYS_DEBUG, False)),
        }

    def initialize_connection(self, connection_params):
        connection = murmur_connection.MurmurConnection(connection_params)
        connection.connect()


if __name__ == "__main__":
    system_args: Dict[str, str] = vars(args_parser.parse_args())
    mumimo = MumimoService(system_args)
