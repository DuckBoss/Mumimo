#!/usr/bin/env python3


from src.mumimo import MumimoService
from src.system_arguments import args_parser
from src.logging import init_logger


if __name__ == "__main__":
    print(vars(args_parser.parse_args()))
    # mumimo = MumimoInitService(vars(args_parser.parse_args()))
    init_logger()
    mumimo = MumimoService(vars(args_parser.parse_args()))
