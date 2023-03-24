import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

from ..constants import VERBOSITY_MIN, EnvArgs, MumimoCfgFields, SysArgs
from ..exceptions import ConfigError
from ..utils import config_utils, connection_utils
from ..utils.parsers import env_parser

if TYPE_CHECKING:
    from ..config import Config


logger = logging.getLogger(__name__)


class MumimoInitService:
    """
    To initialize the mumimo service the following methods need to be run in order:
        Initializations:
        - initialize_config()
        - initialize_client_settings()
        Next Steps:
        - get_connection_parameters() for establishing a murmur connection.
        - get_prioritized_env_options() to get required options for database connection.
    """

    _sys_args: Dict[str, str] = {}
    _prioritized_env_opts: Dict[str, Any] = {}
    _prioritized_cfg_opts: Dict[str, Any] = {}

    def __init__(self, sys_args: Dict[str, str]) -> None:
        self._sys_args = sys_args

    def initialize_config(self) -> "Config":
        # Initialize mumimo config.
        cfg_instance: "Config" = config_utils.initialize_mumimo_config(self._get_sys_args().get(SysArgs.SYS_CONFIG_FILE))
        if cfg_instance is None:
            raise ConfigError("An unexpected error occurred where the config file was not read during initialization.", logger=logger)
        return cfg_instance

    def initialize_client_settings(self, cfg_instance: "Config") -> None:
        # Initialize client settings.
        self._prioritized_cfg_opts = self._get_prioritized_client_config_options(cfg_instance)
        self._prioritized_env_opts = self._get_prioritized_client_env_options()

    def get_connection_parameters(self) -> Dict[str, Any]:
        _prioritized_env_opts = self.get_prioritized_env_options()
        _prioritized_cfg_opts = self.get_prioritized_cfg_options()
        if not _prioritized_cfg_opts or not _prioritized_env_opts:
            return {}

        _sys_args = self._get_sys_args()
        return {
            SysArgs.SYS_HOST: _prioritized_env_opts.get(SysArgs.SYS_HOST),
            SysArgs.SYS_PORT: _prioritized_env_opts.get(SysArgs.SYS_PORT),
            SysArgs.SYS_USER: _prioritized_env_opts.get(SysArgs.SYS_USER),
            SysArgs.SYS_PASS: _prioritized_env_opts.get(SysArgs.SYS_PASS),
            SysArgs.SYS_CERT: _prioritized_env_opts.get(SysArgs.SYS_CERT),
            SysArgs.SYS_KEY: _prioritized_env_opts.get(SysArgs.SYS_KEY),
            SysArgs.SYS_TOKENS: _prioritized_env_opts.get(SysArgs.SYS_TOKENS),
            SysArgs.SYS_SUPER_USER: _prioritized_env_opts.get(SysArgs.SYS_SUPER_USER),
            SysArgs.SYS_VERBOSE: _sys_args.get(SysArgs.SYS_VERBOSE) or VERBOSITY_MIN,
            SysArgs.SYS_RECONNECT: _prioritized_cfg_opts.get(SysArgs.SYS_RECONNECT, False),
        }

    def get_prioritized_cfg_options(self) -> Dict[str, Any]:
        if not self._prioritized_cfg_opts:
            return {}
        return self._prioritized_cfg_opts

    def get_prioritized_env_options(self) -> Dict[str, Any]:
        if not self._prioritized_env_opts:
            return {}
        return self._prioritized_env_opts

    def _get_sys_args(self) -> Dict[str, str]:
        return self._sys_args

    def _get_prioritized_client_config_options(self, cfg_instance: "Config") -> Dict[str, Any]:
        # Consolidate priority between system arguments and config file.
        # System arguments should have higher priority than config file.
        prioritized_options: Dict[str, Any] = {}

        # Prioritize auto-reconnect from system argument over config option.
        reconnect = self._get_sys_args().get(SysArgs.SYS_RECONNECT) or cfg_instance.get(
            MumimoCfgFields.SETTINGS.CONNECTION.AUTO_RECONNECT, fallback=False
        )
        if reconnect is not None:
            prioritized_options[SysArgs.SYS_RECONNECT] = reconnect
            cfg_instance.set(MumimoCfgFields.SETTINGS.CONNECTION.AUTO_RECONNECT, reconnect)

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

        # Prioritize system args from system argument over environment file.
        sys_tokens = self._get_sys_args().get(SysArgs.SYS_TOKENS) or env_args.get(EnvArgs.ENV_TOKENS)
        if isinstance(sys_tokens, str):
            sys_tokens = connection_utils.parse_channel_tokens(sys_tokens)
        prioritized_options[SysArgs.SYS_TOKENS] = sys_tokens

        prioritized_options.update(
            {
                # Prioritize connection args from system arguments over environment file:
                SysArgs.SYS_HOST: self._get_sys_args().get(SysArgs.SYS_HOST) or env_args.get(EnvArgs.ENV_HOST),
                SysArgs.SYS_PORT: self._get_sys_args().get(SysArgs.SYS_PORT) or env_args.get(EnvArgs.ENV_PORT),
                SysArgs.SYS_USER: self._get_sys_args().get(SysArgs.SYS_USER) or env_args.get(EnvArgs.ENV_USER),
                SysArgs.SYS_PASS: self._get_sys_args().get(SysArgs.SYS_PASS) or env_args.get(EnvArgs.ENV_PASS),
                SysArgs.SYS_CERT: self._get_sys_args().get(SysArgs.SYS_CERT) or env_args.get(EnvArgs.ENV_CERT),
                SysArgs.SYS_KEY: self._get_sys_args().get(SysArgs.SYS_KEY) or env_args.get(EnvArgs.ENV_KEY),
                SysArgs.SYS_SUPER_USER: self._get_sys_args().get(SysArgs.SYS_SUPER_USER) or env_args.get(EnvArgs.ENV_SUPER_USER),
                # Prioritize database args from system arguments over environment file:
                SysArgs.SYS_DB_DIALECT: self._get_sys_args().get(SysArgs.SYS_DB_DIALECT) or env_args.get(EnvArgs.ENV_DB_DIALECT),
                SysArgs.SYS_DB_DRIVER: self._get_sys_args().get(SysArgs.SYS_DB_DRIVER) or env_args.get(EnvArgs.ENV_DB_DRIVER),
                SysArgs.SYS_DB_USER: self._get_sys_args().get(SysArgs.SYS_DB_USER) or env_args.get(EnvArgs.ENV_DB_USER),
                SysArgs.SYS_DB_PASS: self._get_sys_args().get(SysArgs.SYS_DB_PASS) or env_args.get(EnvArgs.ENV_DB_PASS),
                SysArgs.SYS_DB_HOST: self._get_sys_args().get(SysArgs.SYS_DB_HOST) or env_args.get(EnvArgs.ENV_DB_HOST),
                SysArgs.SYS_DB_NAME: self._get_sys_args().get(SysArgs.SYS_DB_NAME) or env_args.get(EnvArgs.ENV_DB_NAME),
                SysArgs.SYS_DB_QUERY: self._get_sys_args().get(SysArgs.SYS_DB_QUERY) or env_args.get(EnvArgs.ENV_DB_QUERY),
            }
        )

        return prioritized_options
