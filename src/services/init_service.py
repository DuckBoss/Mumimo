from typing import Dict, Any, Optional

from ..utils import config_utils, env_parser, mumimo_utils
from ..constants import ENV_ARGS, SYS_ARGS, CFG_SECTION, CFG_FIELD, VERBOSITY_MIN
from ..exceptions import ConfigError
from ..config import Config
from ..logging import get_logger

logger = get_logger(__name__)


class MumimoInitService:
    _sys_args: Dict[str, str]

    def __init__(self, sys_args: Dict[str, str]) -> None:
        self._sys_args = sys_args

    def initialize_config(self) -> Config:
        # Initialize mumimo config.
        cfg_instance: Config = config_utils.initialize_mumimo_config(self._sys_args.get(SYS_ARGS.SYS_CONFIG_FILE))
        if cfg_instance is None:
            raise ConfigError("An unexpected error occurred where the config file was not read during initialization.", logger)
        return cfg_instance

    def initialize_client_settings(self, cfg_instance: Config) -> Dict[str, Any]:
        prioritized_cfg_options = self._get_prioritized_client_config_options(cfg_instance)
        cfg_instance.update(prioritized_cfg_options)

        prioritized_env_options = self._get_prioritized_client_env_options()

        return {
            SYS_ARGS.SYS_HOST: prioritized_env_options.get(SYS_ARGS.SYS_HOST),
            SYS_ARGS.SYS_PORT: prioritized_env_options.get(SYS_ARGS.SYS_PORT),
            SYS_ARGS.SYS_USER: prioritized_env_options.get(SYS_ARGS.SYS_USER),
            SYS_ARGS.SYS_PASS: prioritized_env_options.get(SYS_ARGS.SYS_PASS),
            SYS_ARGS.SYS_CERT: prioritized_env_options.get(SYS_ARGS.SYS_CERT),
            SYS_ARGS.SYS_KEY: prioritized_env_options.get(SYS_ARGS.SYS_KEY),
            SYS_ARGS.SYS_TOKENS: prioritized_env_options.get(SYS_ARGS.SYS_TOKENS),
            SYS_ARGS.SYS_VERBOSE: self._sys_args.get(SYS_ARGS.SYS_VERBOSE) or VERBOSITY_MIN,
            SYS_ARGS.SYS_RECONNECT: cfg_instance.get(CFG_SECTION.SETTINGS.CONNECTION, CFG_FIELD.SETTINGS.CONNECTION.AUTO_RECONNECT),
        }

    def _get_prioritized_client_config_options(self, cfg_instance: Config) -> Dict[str, Any]:
        # Consolidate priority between system arguments and config file.
        # System arguments should have higher priority than config file.

        # Prioritize auto-reconnect from system argument over config option.
        prioritized_options: Dict[str, Any] = {}
        reconnect = self._sys_args.get(SYS_ARGS.SYS_RECONNECT) or cfg_instance.get(
            CFG_SECTION.SETTINGS.CONNECTION, CFG_FIELD.SETTINGS.CONNECTION.AUTO_RECONNECT, fallback=False
        )
        if reconnect is not None:
            prioritized_options[CFG_FIELD.SETTINGS.CONNECTION.AUTO_RECONNECT] = reconnect

        return prioritized_options

    def _get_prioritized_client_env_options(self) -> Dict[str, Any]:
        # Load in options from .env file if present.
        available_env_file: Optional[str] = self._sys_args.get(SYS_ARGS.SYS_ENV_FILE)
        env_args: Dict[str, Any] = {}
        if available_env_file is not None:
            env_args = env_parser.read_env_file(available_env_file)

        prioritized_options: Dict[str, Any] = {}
        # Load in remaining options from system arguments, and prioritize system args
        sys_tokens = self._sys_args.get(SYS_ARGS.SYS_TOKENS) or env_args.get(ENV_ARGS.ENV_TOKENS)
        if isinstance(sys_tokens, str):
            sys_tokens = mumimo_utils.parse_channel_tokens(sys_tokens)
        prioritized_options[SYS_ARGS.SYS_TOKENS] = sys_tokens

        prioritized_options.update(
            {
                SYS_ARGS.SYS_HOST: self._sys_args.get(SYS_ARGS.SYS_HOST) or env_args.get(ENV_ARGS.ENV_HOST),
                SYS_ARGS.SYS_PORT: self._sys_args.get(SYS_ARGS.SYS_PORT) or env_args.get(ENV_ARGS.ENV_PORT),
                SYS_ARGS.SYS_USER: self._sys_args.get(SYS_ARGS.SYS_USER) or env_args.get(ENV_ARGS.ENV_USER),
                SYS_ARGS.SYS_PASS: self._sys_args.get(SYS_ARGS.SYS_PASS) or env_args.get(ENV_ARGS.ENV_PASS),
                SYS_ARGS.SYS_CERT: self._sys_args.get(SYS_ARGS.SYS_CERT) or env_args.get(ENV_ARGS.ENV_CERT),
                SYS_ARGS.SYS_KEY: self._sys_args.get(SYS_ARGS.SYS_KEY) or env_args.get(ENV_ARGS.ENV_KEY),
            }
        )

        return prioritized_options
