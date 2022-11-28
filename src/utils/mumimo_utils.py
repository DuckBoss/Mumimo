import platform
from argparse import ArgumentTypeError
from typing import Any, Dict, List, Optional

from ..config import Config
from ..constants import (
    CFG_FIELD_RECONNECT,
    CFG_FIELD_VERBOSE,
    CFG_SECTION_MAIN,
    ENV_CERT,
    ENV_HOST,
    ENV_KEY,
    ENV_PASS,
    ENV_PORT,
    ENV_TOKENS,
    ENV_USER,
    SYS_CERT,
    SYS_CONFIG_FILE,
    SYS_ENV_FILE,
    SYS_HOST,
    SYS_KEY,
    SYS_PASS,
    SYS_PORT,
    SYS_RECONNECT,
    SYS_TOKENS,
    SYS_USER,
    SYS_VERBOSE,
    VERBOSITY_MAX,
    VERBOSITY_MIN,
)
from ..exceptions import ConfigError
from . import config_utils, env_parser


def is_supported_platform() -> bool:
    return platform.system() in ("Linux", "Darwin")


def validate_verbose_level(level: str):
    if level is None:
        return 0
    value = None
    try:
        value = int(level)
    except ValueError as exc:
        raise ArgumentTypeError(f"The verbose level must be a value between {VERBOSITY_MIN} and {VERBOSITY_MAX}") from exc
    value = max(value, VERBOSITY_MIN)
    value = min(value, VERBOSITY_MAX)
    return value


def parse_channel_tokens(tokens: str) -> Optional[List[str]]:
    if not isinstance(tokens, str):
        return None
    tokens = tokens.strip()
    if not tokens:
        return None
    tokens = " ".join(tokens.split())
    return [token.strip() for token in tokens.split()]


def get_prioritized_client_config_options(sys_args: Dict[str, Any], cfg_instance: Config) -> Dict[str, Any]:
    # Consolidate priority between system arguments and config file.
    # System arguments should have higher priority than config file.
    prioritized_options: Dict[str, Any] = {CFG_SECTION_MAIN: {}}
    verbose_level = sys_args.get(SYS_VERBOSE) or cfg_instance.get(CFG_SECTION_MAIN, CFG_FIELD_VERBOSE)
    if verbose_level is not None:
        verbose_level = validate_verbose_level(str(verbose_level))
        prioritized_options[CFG_SECTION_MAIN][CFG_FIELD_VERBOSE] = verbose_level
    reconnect = sys_args.get(SYS_RECONNECT) or cfg_instance.get(CFG_SECTION_MAIN, CFG_FIELD_RECONNECT)
    if reconnect is not None:
        prioritized_options[CFG_SECTION_MAIN][CFG_FIELD_RECONNECT] = reconnect
    return prioritized_options


def get_prioritized_client_env_options(sys_args: Dict[str, Any]) -> Dict[str, Any]:
    # Load in options from .env file if present.
    available_env_file: Optional[str] = sys_args.get(SYS_ENV_FILE)
    env_args: Dict[str, Any] = {}
    if available_env_file is not None:
        env_args = env_parser.read_env_file(available_env_file)

    prioritized_options: Dict[str, Any] = {}
    # Load in remaining options from system arguments, and prioritize system args
    sys_tokens = sys_args.get(SYS_TOKENS) or env_args.get(ENV_TOKENS)
    if isinstance(sys_tokens, str):
        sys_tokens = parse_channel_tokens(sys_tokens)
    prioritized_options[SYS_TOKENS] = sys_tokens

    prioritized_options.update(
        {
            SYS_HOST: sys_args.get(SYS_HOST) or env_args.get(ENV_HOST),
            SYS_PORT: sys_args.get(SYS_PORT) or env_args.get(ENV_PORT),
            SYS_USER: sys_args.get(SYS_USER) or env_args.get(ENV_USER),
            SYS_PASS: sys_args.get(SYS_PASS) or env_args.get(ENV_PASS),
            SYS_CERT: sys_args.get(SYS_CERT) or env_args.get(ENV_CERT),
            SYS_KEY: sys_args.get(SYS_KEY) or env_args.get(ENV_KEY),
        }
    )

    return prioritized_options


# Maybe also move this to a different file... 'src/initialize.py'?
def initialize_client_settings(sys_args: Dict[str, str]) -> Dict[str, Any]:
    # Initialize mumimo config.
    _config_instance = config_utils.initialize_mumimo_config(sys_args.get(SYS_CONFIG_FILE))
    if _config_instance is None:
        raise ConfigError("An unexpected error occurred where the config file was not read during initialization.")

    prioritized_cfg_options = get_prioritized_client_config_options(sys_args, _config_instance)
    _config_instance.update(prioritized_cfg_options)

    prioritized_env_options = get_prioritized_client_env_options(sys_args)

    return {
        SYS_HOST: prioritized_env_options.get(SYS_HOST),
        SYS_PORT: prioritized_env_options.get(SYS_PORT),
        SYS_USER: prioritized_env_options.get(SYS_USER),
        SYS_PASS: prioritized_env_options.get(SYS_PASS),
        SYS_CERT: prioritized_env_options.get(SYS_CERT),
        SYS_KEY: prioritized_env_options.get(SYS_KEY),
        SYS_TOKENS: prioritized_env_options.get(SYS_TOKENS),
        SYS_RECONNECT: _config_instance.get(CFG_SECTION_MAIN, CFG_FIELD_RECONNECT),
        SYS_VERBOSE: _config_instance.get(CFG_SECTION_MAIN, CFG_FIELD_VERBOSE),
    }
