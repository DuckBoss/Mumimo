# Verbosity Constants
VERBOSE_NONE: int = 0
VERBOSE_MIN: int = 1
VERBOSE_STANDARD: int = 2
VERBOSE_HIGH: int = 3
VERBOSE_MAX: int = 4
VERBOSITY_MIN: int = VERBOSE_NONE
VERBOSITY_MAX: int = VERBOSE_MAX


# Logging Output Identifier Constants
class LogOutputIdentifiers:
    PLUGINS: str = "Plugins"
    PLUGINS_PERMISSIONS: str = f"{PLUGINS}.Permissions"
    PLUGINS_COMMANDS: str = f"{PLUGINS}.Commands"
    PLUGINS_PARAMETERS: str = f"{PLUGINS}.Parameters"

    DB: str = "Database"
    DB_PERMISSIONS: str = f"{DB}.Permissions"
    DB_USERS: str = f"{DB}.Users"
    DB_ALIASES: str = f"{DB}.Aliases"
    DB_PLUGINS: str = f"{DB}.Plugins"
    DB_PLUGINS_COMMANDS: str = f"{DB}.{PLUGINS}.Commands"
    DB_PLUGINS_PERMISSIONS: str = f"{DB}.{PLUGINS}.Permissions"

    MUMBLE: str = "Mumble"
    MUMBLE_ON_CONNECT: str = f"{MUMBLE}.On_Connect"
    MUMBLE_ON_DISCONNECT: str = f"{MUMBLE}.On_Disconnect"


# Env Args Constants
class EnvArgs:
    ENV_HOST: str = "MUMIMO_HOST"
    ENV_PORT: str = "MUMIMO_PORT"
    ENV_USER: str = "MUMIMO_USER"
    ENV_PASS: str = "MUMIMO_PASS"
    ENV_CERT: str = "MUMIMO_CERT"
    ENV_KEY: str = "MUMIMO_KEY"
    ENV_TOKENS: str = "MUMIMO_TOKENS"
    ENV_SUPER_USER: str = "MUMIMO_SUPER_USER"
    ENV_DB_DIALECT: str = "MUMIMO_DB_DIALECT"
    ENV_DB_DRIVER: str = "MUMIMO_DB_DRIVER"
    ENV_DB_USER: str = "MUMIMO_DB_USER"
    ENV_DB_PASS: str = "MUMIMO_DB_PASS"
    ENV_DB_HOST: str = "MUMIMO_DB_HOST"
    ENV_DB_PORT: str = "MUMIMO_DB_PORT"
    ENV_DB_NAME: str = "MUMIMO_DB_NAME"


# Sys Args Constants
class SysArgs:
    SYS_HOST: str = "host"
    SYS_PORT: str = "port"
    SYS_USER: str = "user"
    SYS_PASS: str = "password"
    SYS_CERT: str = "cert_file"
    SYS_KEY: str = "key_file"
    SYS_TOKENS: str = "tokens"
    SYS_VERBOSE: str = "verbose"
    SYS_RECONNECT: str = "auto_reconnect"
    SYS_GEN_CERT: str = "generate_cert"
    SYS_SUPER_USER: str = "superuser"
    SYS_NAME: str = "name"
    SYS_ENV_FILE: str = "env_file"
    SYS_CONFIG_FILE: str = "config_file"
    SYS_LOG_CONFIG_FILE: str = "log_config_file"
    SYS_GUI_THEMES_FILE: str = "gui_themes_file"
    SYS_DB_LOCALDBPATH: str = "local_database_path"
    SYS_DB_LOCALDBDIALECT: str = "local_database_dialect"
    SYS_DB_LOCALDBDRIVER: str = "local_database_driver"
    SYS_DB_USEREMOTEDB: str = "use_remote_database"
    SYS_DB_DIALECT: str = "db_dialect"
    SYS_DB_DRIVER: str = "db_driver"
    SYS_DB_USER: str = "db_user"
    SYS_DB_PASS: str = "db_pass"
    SYS_DB_HOST: str = "db_host"
    SYS_DB_PORT: str = "db_port"
    SYS_DB_NAME: str = "db_name"
    SYS_PLUGINS_PATH: str = "plugins_path"
    SYS_PLUGINS_CONFIG_PATH: str = "plugins_config_path"


# Config Constants
DEFAULT_PATH_CONFIG_FILE: str = "config/config.toml"
DEFAULT_PATH_LOGGING_CONFIG_FILE: str = "config/logging.toml"
DEFAULT_PATH_GUI_THEMES_FILE: str = "config/gui_themes.toml"


class DefaultPermissionGroups:
    DEFAULT_NONE = "none"
    DEFAULT_GUEST = "guest"
    DEFAULT_MEMBER = "member"
    DEFAULT_ADMIN = "admin"


class PluginCfgSections:
    PLUGIN: str = "plugin"
    PLUGIN_ABOUT: str = f"{PLUGIN}.about"
    PLUGIN_SETTINGS: str = f"{PLUGIN}.settings"
    PLUGIN_COMMANDS: str = f"{PLUGIN}.commands"
    PLUGIN_HELP: str = f"{PLUGIN}.help"


class PluginCfgFields:
    class PLUGIN:
        ENABLED: str = f"{PluginCfgSections.PLUGIN}.enabled"

        class ABOUT:
            NAME: str = f"{PluginCfgSections.PLUGIN_ABOUT}.name"
            VERSION: str = f"{PluginCfgSections.PLUGIN_ABOUT}.version"
            DESCRIPTION: str = f"{PluginCfgSections.PLUGIN_ABOUT}.description"

        class SETTINGS:
            pass

        class COMMANDS:
            DISABLE_COMMANDS: str = f"{PluginCfgSections.PLUGIN_COMMANDS}.disable_commands"
            DISABLE_PARAMETERS: str = f"{PluginCfgSections.PLUGIN_COMMANDS}.disable_parameters"
            DEFAULT_PERMISSION_GROUPS: str = f"{PluginCfgSections.PLUGIN_COMMANDS}.default_permission_groups"

        class HELP:
            COMMANDS_HELP_TEXT: str = f"{PluginCfgSections.PLUGIN_HELP}.commands_help_text"


class LogCfgSections:
    # Log Config Sections
    OUTPUT: str = "output"
    OUTPUT_FILE: str = f"{OUTPUT}.file"
    OUTPUT_CONSOLE: str = f"{OUTPUT}.console"
    OUTPUT_FILE_PRIVACY: str = f"{OUTPUT_FILE}.privacy"
    OUTPUT_CONSOLE_PRIVACY: str = f"{OUTPUT_CONSOLE}.privacy"


class LogCfgFields:
    # Log Config Fields
    class OUTPUT:
        class FILE:
            ENABLE: str = f"{LogCfgSections.OUTPUT_FILE}.enable"
            LEVEL: str = f"{LogCfgSections.OUTPUT_FILE}.level"
            PATH: str = f"{LogCfgSections.OUTPUT_FILE}.path"
            FORMAT: str = f"{LogCfgSections.OUTPUT_FILE}.format"
            NAME: str = f"{LogCfgSections.OUTPUT_FILE}.name"

            class PRIVACY:
                REDACT_MESSAGE: str = f"{LogCfgSections.OUTPUT_FILE_PRIVACY}.redact_message"
                REDACT_COMMANDS: str = f"{LogCfgSections.OUTPUT_FILE_PRIVACY}.redact_commands"
                REDACT_CHANNEL: str = f"{LogCfgSections.OUTPUT_FILE_PRIVACY}.redact_channel"
                REDACT_USER: str = f"{LogCfgSections.OUTPUT_FILE_PRIVACY}.redact_user"

        class CONSOLE:
            FORMAT: str = f"{LogCfgSections.OUTPUT_CONSOLE}.format"

            class PRIVACY:
                REDACT_MESSAGE: str = f"{LogCfgSections.OUTPUT_CONSOLE_PRIVACY}.redact_message"
                REDACT_COMMANDS: str = f"{LogCfgSections.OUTPUT_CONSOLE_PRIVACY}.redact_commands"
                REDACT_CHANNEL: str = f"{LogCfgSections.OUTPUT_CONSOLE_PRIVACY}.redact_channel"
                REDACT_USER: str = f"{LogCfgSections.OUTPUT_CONSOLE_PRIVACY}.redact_user"


class MumimoCfgSections:
    # Mumimo Config Sections
    SETTINGS: str = "settings"
    SETTINGS_MEDIA: str = f"{SETTINGS}.media"
    SETTINGS_CONNECTION: str = f"{SETTINGS}.connection"
    SETTINGS_DATABASE: str = f"{SETTINGS}.database"
    SETTINGS_COMMANDS: str = f"{SETTINGS}.commands"
    SETTINGS_MEDIA: str = f"{SETTINGS}.media"
    SETTINGS_MEDIA_AUDIODUCKING: str = f"{SETTINGS_MEDIA}.audio_ducking"
    SETTINGS_MEDIA_YOUTUBEDL: str = f"{SETTINGS_MEDIA}.youtube_dl"
    SETTINGS_PLUGINS: str = f"{SETTINGS}.plugins"
    SETTINGS_GUI: str = f"{SETTINGS}.gui"

    OUTPUT: str = "output"
    OUTPUT_GUI: str = f"{OUTPUT}.gui"
    OUTPUT_GUI_CANVAS: str = f"{OUTPUT_GUI}.canvas"
    OUTPUT_GUI_TEXT: str = f"{OUTPUT_GUI}.text"


class MumimoCfgFields:
    # Mumimo Config Fields
    class SETTINGS:
        class CONNECTION:
            MUTE: str = f"{MumimoCfgSections.SETTINGS_CONNECTION}.mute"
            DEAFEN: str = f"{MumimoCfgSections.SETTINGS_CONNECTION}.deafen"
            REGISTER: str = f"{MumimoCfgSections.SETTINGS_CONNECTION}.register"
            COMMENT: str = f"{MumimoCfgSections.SETTINGS_CONNECTION}.comment"
            DEFAULT_CHANNEL: str = f"{MumimoCfgSections.SETTINGS_CONNECTION}.default_channel"
            AUTO_RECONNECT: str = f"{MumimoCfgSections.SETTINGS_CONNECTION}.auto_reconnect"
            NAME: str = f"{MumimoCfgSections.SETTINGS_CONNECTION}.name"

        class DATABASE:
            USE_REMOTE_DB: str = f"{MumimoCfgSections.SETTINGS_DATABASE}.use_remote_database"
            LOCAL_DB_PATH: str = f"{MumimoCfgSections.SETTINGS_DATABASE}.local_database_path"
            LOCAL_DB_DIALECT: str = f"{MumimoCfgSections.SETTINGS_DATABASE}.local_database_dialect"
            LOCAL_DB_DRIVERNAME: str = f"{MumimoCfgSections.SETTINGS_DATABASE}.local_database_driver"
            DEFAULT_PERMISSION_GROUPS: str = f"{MumimoCfgSections.SETTINGS_DATABASE}.default_permission_groups"
            DEFAULT_ALIASES: str = f"{MumimoCfgSections.SETTINGS_DATABASE}.default_aliases"

        class COMMANDS:
            TOKEN: str = f"{MumimoCfgSections.SETTINGS_COMMANDS}.command_token"
            TICK_RATE: str = f"{MumimoCfgSections.SETTINGS_COMMANDS}.command_tick_rate"
            MAX_MULTI_COMMAND_LENGTH: str = f"{MumimoCfgSections.SETTINGS_COMMANDS}.max_multi_command_length"
            MAX_COMMAND_QUEUE_LENGTH: str = f"{MumimoCfgSections.SETTINGS_COMMANDS}.max_command_queue_length"
            COMMAND_HISTORY_LENGTH: str = f"{MumimoCfgSections.SETTINGS_COMMANDS}.command_history_length"

        class MEDIA:
            VOLUME: str = f"{MumimoCfgSections.SETTINGS_MEDIA}.volume"
            STEREO_AUDIO: str = f"{MumimoCfgSections.SETTINGS_MEDIA}.stereo_audio"
            MAX_QUEUE_LENGTH: str = f"{MumimoCfgSections.SETTINGS_MEDIA}.max_queue_length"
            FFMPEG_PATH: str = f"{MumimoCfgSections.SETTINGS_MEDIA}.ffmpeg_path"
            VLC_PATH: str = f"{MumimoCfgSections.SETTINGS_MEDIA}.vlc_path"
            MEDIA_DIRECTORY: str = f"{MumimoCfgSections.SETTINGS_MEDIA}.media_directory"

            class AUDIODUCKING:
                ENABLE: str = f"{MumimoCfgSections.SETTINGS_MEDIA_AUDIODUCKING}.enable"
                VOLUME: str = f"{MumimoCfgSections.SETTINGS_MEDIA_AUDIODUCKING}.volume"
                THRESHOLD: str = f"{MumimoCfgSections.SETTINGS_MEDIA_AUDIODUCKING}.threshold"
                DELAY: str = f"{MumimoCfgSections.SETTINGS_MEDIA_AUDIODUCKING}.delay"

            class YOUTUBEDL:
                PROXY_URL: str = f"{MumimoCfgSections.SETTINGS_MEDIA_YOUTUBEDL}.proxy_url"
                COOKIE_FILE: str = f"{MumimoCfgSections.SETTINGS_MEDIA_YOUTUBEDL}.cookie_file"

        class PLUGINS:
            PLUGINS_PATH: str = f"{MumimoCfgSections.SETTINGS_PLUGINS}.plugins_path"
            PLUGINS_CUSTOM_PATH: str = f"{MumimoCfgSections.SETTINGS_PLUGINS}.custom_plugins_path"
            PLUGINS_CONFIG_PATH: str = f"{MumimoCfgSections.SETTINGS_PLUGINS}.plugins_config_path"
            DISABLED_PLUGINS: str = f"{MumimoCfgSections.SETTINGS_PLUGINS}.disabled_plugins"
            SAFE_MODE_PLUGINS: str = f"{MumimoCfgSections.SETTINGS_PLUGINS}.safe_mode_plugins"

        class GUI:
            ENABLE: str = f"{MumimoCfgSections.SETTINGS_GUI}.enable"
            THEMES_PATH: str = f"{MumimoCfgSections.SETTINGS_GUI}.themes_path"
            SELECTED_THEME: str = f"{MumimoCfgSections.SETTINGS_GUI}.selected_theme"

    class OUTPUT:
        class GUI:
            ENABLE: str = f"{MumimoCfgSections.OUTPUT_GUI}.enable"

            class CANVAS:
                BACKGROUND_COLOR: str = f"{MumimoCfgSections.OUTPUT_GUI_CANVAS}.background_color"
                IMAGE_BACKGROUND_COLOR: str = f"{MumimoCfgSections.OUTPUT_GUI_CANVAS}.image_background_color"
                CONTENT_ALIGNMENT: str = f"{MumimoCfgSections.OUTPUT_GUI_CANVAS}.content_alignment"
                BORDER: str = f"{MumimoCfgSections.OUTPUT_GUI_CANVAS}.border"

            class TEXT:
                FONT: str = f"{MumimoCfgSections.OUTPUT_GUI_TEXT}.font"
                STANDARD_TEXT_COLOR: str = f"{MumimoCfgSections.OUTPUT_GUI_TEXT}.standard_text_color"
                HEADER_TEXT_COLOR: str = f"{MumimoCfgSections.OUTPUT_GUI_TEXT}.header_text_color"
                SUB_HEADER_TEXT_COLOR: str = f"{MumimoCfgSections.OUTPUT_GUI_TEXT}.sub_header_text_color"
                INDEX_TEXT_COLOR: str = f"{MumimoCfgSections.OUTPUT_GUI_TEXT}.index_text_Color"
