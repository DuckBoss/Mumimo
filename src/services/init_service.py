from typing import Any, Dict, Optional

from ..config import Config
from ..constants import VERBOSITY_MIN, EnvArgs, MumimoCfgFields, SysArgs
from ..exceptions import ConfigError
from ..logging import get_logger
from ..utils import config_utils, mumimo_utils
from ..utils.parsers import env_parser

logger = get_logger(__name__)


class MumimoInitService:
    _sys_args: Dict[str, str]

    def __init__(self, sys_args: Dict[str, str]) -> None:
        self._sys_args = sys_args

    def initialize_config(self) -> Config:
        # Initialize mumimo config.
        cfg_instance: Config = config_utils.initialize_mumimo_config(self._get_sys_args().get(SysArgs.SYS_CONFIG_FILE))
        if cfg_instance is None:
            raise ConfigError("An unexpected error occurred where the config file was not read during initialization.", logger)
        return cfg_instance

    def initialize_client_settings(self, cfg_instance: Config) -> Dict[str, Any]:
        prioritized_cfg_options: Dict[str, Any] = self._get_prioritized_client_config_options(cfg_instance)
        # cfg_instance.update(prioritized_cfg_options)

        prioritized_env_options: Dict[str, Any] = self._get_prioritized_client_env_options()

        return {
            SysArgs.SYS_HOST: prioritized_env_options.get(SysArgs.SYS_HOST),
            SysArgs.SYS_PORT: prioritized_env_options.get(SysArgs.SYS_PORT),
            SysArgs.SYS_USER: prioritized_env_options.get(SysArgs.SYS_USER),
            SysArgs.SYS_PASS: prioritized_env_options.get(SysArgs.SYS_PASS),
            SysArgs.SYS_CERT: prioritized_env_options.get(SysArgs.SYS_CERT),
            SysArgs.SYS_KEY: prioritized_env_options.get(SysArgs.SYS_KEY),
            SysArgs.SYS_TOKENS: prioritized_env_options.get(SysArgs.SYS_TOKENS),
            SysArgs.SYS_SUPER_USER: prioritized_env_options.get(SysArgs.SYS_SUPER_USER),
            SysArgs.SYS_VERBOSE: self._get_sys_args().get(SysArgs.SYS_VERBOSE) or VERBOSITY_MIN,
            SysArgs.SYS_RECONNECT: prioritized_cfg_options.get(SysArgs.SYS_RECONNECT, False),
        }

    def _get_sys_args(self) -> Dict[str, str]:
        return self._sys_args

    def _get_prioritized_client_config_options(self, cfg_instance: Config) -> Dict[str, Any]:
        # Consolidate priority between system arguments and config file.
        # System arguments should have higher priority than config file.

        # Prioritize auto-reconnect from system argument over config option.
        prioritized_options: Dict[str, Any] = {}

        reconnect = self._get_sys_args().get(SysArgs.SYS_RECONNECT) or cfg_instance.get(
            MumimoCfgFields.SETTINGS.CONNECTION.AUTO_RECONNECT, fallback=False
        )
        if reconnect is not None:
            prioritized_options[SysArgs.SYS_RECONNECT] = reconnect

        return prioritized_options

    def _get_prioritized_client_env_options(self) -> Dict[str, Any]:
        # Load in options from .env file if present.
        available_env_file: Optional[str] = self._get_sys_args().get(SysArgs.SYS_ENV_FILE, None) or ".env"
        env_args: Dict[str, Any] = {}
        if available_env_file is not None:
            env_args = env_parser.read_env_file(available_env_file)
            if env_args is None:
                env_args = {}

        prioritized_options: Dict[str, Any] = {}
        # Load in remaining options from system arguments, and prioritize system args
        sys_tokens = self._get_sys_args().get(SysArgs.SYS_TOKENS) or env_args.get(EnvArgs.ENV_TOKENS)
        if isinstance(sys_tokens, str):
            sys_tokens = mumimo_utils.parse_channel_tokens(sys_tokens)
        prioritized_options[SysArgs.SYS_TOKENS] = sys_tokens

        prioritized_options.update(
            {
                SysArgs.SYS_HOST: self._get_sys_args().get(SysArgs.SYS_HOST) or env_args.get(EnvArgs.ENV_HOST),
                SysArgs.SYS_PORT: self._get_sys_args().get(SysArgs.SYS_PORT) or env_args.get(EnvArgs.ENV_PORT),
                SysArgs.SYS_USER: self._get_sys_args().get(SysArgs.SYS_USER) or env_args.get(EnvArgs.ENV_USER),
                SysArgs.SYS_PASS: self._get_sys_args().get(SysArgs.SYS_PASS) or env_args.get(EnvArgs.ENV_PASS),
                SysArgs.SYS_CERT: self._get_sys_args().get(SysArgs.SYS_CERT) or env_args.get(EnvArgs.ENV_CERT),
                SysArgs.SYS_KEY: self._get_sys_args().get(SysArgs.SYS_KEY) or env_args.get(EnvArgs.ENV_KEY),
                SysArgs.SYS_SUPER_USER: self._get_sys_args().get(SysArgs.SYS_SUPER_USER) or env_args.get(EnvArgs.ENV_SUPER_USER),
            }
        )

        return prioritized_options
