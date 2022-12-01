# Env Args Constants
ENV_HOST: str = "MUMIMO_HOST"
ENV_PORT: str = "MUMIMO_PORT"
ENV_USER: str = "MUMIMO_USER"
ENV_PASS: str = "MUMIMO_PASS"
ENV_CERT: str = "MUMIMO_CERT"
ENV_KEY: str = "MUMIMO_KEY"
ENV_TOKENS: str = "MUMIMO_TOKENS"

# Sys Args Constants
SYS_HEADLESS: str = "headless"
SYS_HOST: str = "host"
SYS_PORT: str = "port"
SYS_USER: str = "user"
SYS_PASS: str = "password"
SYS_CERT: str = "cert_file"
SYS_KEY: str = "key_file"
SYS_TOKENS: str = "tokens"
SYS_VERBOSE: str = "verbose"
SYS_RECONNECT: str = "reconnect"
SYS_GEN_CERT: str = "generate_cert"
SYS_SUPER_USER: str = "superuser"
SYS_ENV_FILE: str = "env_file"
SYS_CONFIG_FILE: str = "config_file"

# Config Constants
DEFAULT_PATH_CONFIG_FILE: str = "config/config.toml"
CFG_SECTION_MAIN: str = "main"
CFG_FIELD_MUTE: str = "mute"
CFG_FIELD_DEAFEN: str = "deafen"
CFG_FIELD_REGISTER: str = "register"
CFG_FIELD_COMMENT: str = "commment"
CFG_FIELD_RECONNECT: str = SYS_RECONNECT
CFG_FIELD_VERBOSE: str = SYS_VERBOSE

# Verbosity Constants
VERBOSE_NONE: int = 0
VERBOSE_MIN: int = 1
VERBOSE_STANDARD: int = 2
VERBOSE_PLUS: int = 3
VERBOSE_MUMBLE: int = 4
VERBOSE_MAX: int = 5
VERBOSITY_MIN: int = VERBOSE_NONE
VERBOSITY_MAX: int = VERBOSE_MAX
