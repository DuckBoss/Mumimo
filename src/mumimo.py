from typing import Dict, Optional

from system_arguments import args_parser
from utils import env_parser


class MumimoService:
    def __init__(self, sys_args: Dict[str, str]):
        print(sys_args)
        self.interpret_sys_args(sys_args)

    def interpret_sys_args(self, sys_args: Dict[str, str]):
        available_env_file: Optional[str] = sys_args.get("env_file")
        if available_env_file is not None:
            env_contents = env_parser.read_env_file(available_env_file)
            print(env_contents.items())


if __name__ == "__main__":
    system_args: Dict[str, str] = vars(args_parser.parse_args())
    mumimo = MumimoService(system_args)
