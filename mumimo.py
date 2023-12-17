#!/usr/bin/env python3
from src.logging import init_logger
from src.system_arguments import args_parser
from src.mumimo import MumimoService

def run():
    sys_args = vars(args_parser.parse_args())
    init_logger(sys_args)
    MumimoService(sys_args)

if __name__ == "__main__":
    run()
