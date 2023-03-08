# Verbosity Constants
VERBOSE_NONE: int = 0
VERBOSE_MIN: int = 1
VERBOSE_STANDARD: int = 2
VERBOSE_MAX: int = 3
VERBOSITY_MIN: int = VERBOSE_NONE
VERBOSITY_MAX: int = VERBOSE_MAX


# Env Args Constants
class ENV_ARGS:
    ENV_HOST: str = "MUMIMO_HOST"
    ENV_PORT: str = "MUMIMO_PORT"
    ENV_USER: str = "MUMIMO_USER"
    ENV_PASS: str = "MUMIMO_PASS"
    ENV_CERT: str = "MUMIMO_CERT"
    ENV_KEY: str = "MUMIMO_KEY"
    ENV_TOKENS: str = "MUMIMO_TOKENS"
    ENV_SUPER_USER: str = "MUMIMO_SUPER_USER"


# Sys Args Constants
class SYS_ARGS:
    SYS_HEADLESS: str = "headless"
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
    SYS_ENV_FILE: str = "env_file"
    SYS_CONFIG_FILE: str = "config_file"
    SYS_LOG_CONFIG_FILE: str = "log_config_file"


# Config Constants
DEFAULT_PATH_CONFIG_FILE: str = "config/config.toml"
DEFAULT_PATH_LOGGING_CONFIG_FILE: str = "config/logging.toml"


class LOG_CFG_SECTIONS:
    # Log Config Sections
    OUTPUT: str = "output"
    FILE: str = "file"
    CONSOLE: str = "console"


class LOG_CFG_FIELDS:
    # Log Config Fields
    class OUTPUT:
        class FILE:
            ENABLE: str = "enable"
            LEVEL: str = "level"
            PATH: str = "path"
            FORMAT: str = "format"
            NAME: str = "name"
            MAX_LOGS: str = "max_logs"
            MAX_BYTES: str = "max_bytes"
            MESSAGE_PRIVACY: str = "message_privacy"
            ENABLE_STACK_TRACE: str = "enable_stack_trace"

        class CONSOLE:
            FORMAT: str = "format"
            MESSAGE_PRIVACY: str = "message_privacy"


class MUMIMO_CFG_SECTIONS:
    # Mumimo Config Sections
    SETTINGS: str = "settings"
    SETTINGS_MEDIA: str = f"{SETTINGS}.media"
    SETTINGS_CONNECTION: str = f"{SETTINGS}.connection"
    SETTINGS_COMMANDS: str = f"{SETTINGS}.commands"
    SETTINGS_MEDIA: str = f"{SETTINGS}.media"
    SETTINGS_MEDIA_AUDIODUCKING: str = f"{SETTINGS_MEDIA}.audio_ducking"
    SETTINGS_MEDIA_YOUTUBEDL: str = f"{SETTINGS_MEDIA}.youtube_dl"
    SETTINGS_PLUGINS: str = f"{SETTINGS}.plugins"

    OUTPUT: str = "output"
    OUTPUT_GUI: str = f"{OUTPUT}.gui"
    OUTPUT_GUI_CANVAS: str = f"{OUTPUT_GUI}.canvas"
    OUTPUT_GUI_TEXT: str = f"{OUTPUT_GUI}.text"


class MUMIMO_CFG_FIELDS:
    # Mumimo Config Fields
    class SETTINGS:
        class CONNECTION:
            MUTE: str = f"{MUMIMO_CFG_SECTIONS.SETTINGS_CONNECTION}.mute"
            DEAFEN: str = f"{MUMIMO_CFG_SECTIONS.SETTINGS_CONNECTION}.deafen"
            REGISTER: str = f"{MUMIMO_CFG_SECTIONS.SETTINGS_CONNECTION}.register"
            COMMENT: str = f"{MUMIMO_CFG_SECTIONS.SETTINGS_CONNECTION}.comment"
            DEFAULT_CHANNEL: str = f"{MUMIMO_CFG_SECTIONS.SETTINGS_CONNECTION}.default_channel"
            AUTO_RECONNECT: str = f"{MUMIMO_CFG_SECTIONS.SETTINGS_CONNECTION}.auto_reconnect"

        class COMMANDS:
            TOKEN: str = f"{MUMIMO_CFG_SECTIONS.SETTINGS_COMMANDS}.command_token"
            TICK_RATE: str = f"{MUMIMO_CFG_SECTIONS.SETTINGS_COMMANDS}.command_tick_rate"
            MAX_MULTI_COMMAND_LENGTH: str = f"{MUMIMO_CFG_SECTIONS.SETTINGS_COMMANDS}.max_multi_command_length"
            MAX_COMMAND_QUEUE_LENGTH: str = f"{MUMIMO_CFG_SECTIONS.SETTINGS_COMMANDS}.max_command_queue_length"
            MESSAGE_HISTORY_LENGTH: str = f"{MUMIMO_CFG_SECTIONS.SETTINGS_COMMANDS}.message_history_length"

        class MEDIA:
            VOLUME: str = f"{MUMIMO_CFG_SECTIONS.SETTINGS_MEDIA}.volume"
            STEREO_AUDIO: str = f"{MUMIMO_CFG_SECTIONS.SETTINGS_MEDIA}.stereo_audio"
            MAX_QUEUE_LENGTH: str = f"{MUMIMO_CFG_SECTIONS.SETTINGS_MEDIA}.max_queue_length"
            FFMPEG_PATH: str = f"{MUMIMO_CFG_SECTIONS.SETTINGS_MEDIA}.ffmpeg_path"
            VLC_PATH: str = f"{MUMIMO_CFG_SECTIONS.SETTINGS_MEDIA}.vlc_path"
            MEDIA_DIRECTORY: str = f"{MUMIMO_CFG_SECTIONS.SETTINGS_MEDIA}.media_directory"

            class AUDIO_DUCKING:
                ENABLE: str = f"{MUMIMO_CFG_SECTIONS.SETTINGS_MEDIA_AUDIODUCKING}.enable"
                VOLUME: str = f"{MUMIMO_CFG_SECTIONS.SETTINGS_MEDIA_AUDIODUCKING}.volume"
                THRESHOLD: str = f"{MUMIMO_CFG_SECTIONS.SETTINGS_MEDIA_AUDIODUCKING}.threshold"
                DELAY: str = f"{MUMIMO_CFG_SECTIONS.SETTINGS_MEDIA_AUDIODUCKING}.delay"

            class YOUTUBE_DL:
                PROXY_URL: str = f"{MUMIMO_CFG_SECTIONS.SETTINGS_MEDIA_YOUTUBEDL}.proxy_url"
                COOKIE_FILE: str = f"{MUMIMO_CFG_SECTIONS.SETTINGS_MEDIA_YOUTUBEDL}.cookie_file"

        class PLUGINS:
            DISABLED_PLUGINS: str = f"{MUMIMO_CFG_SECTIONS.SETTINGS_PLUGINS}.disabled_plugins"
            SAFE_MODE_PLUGINS: str = f"{MUMIMO_CFG_SECTIONS.SETTINGS_PLUGINS}.safe_mode_plugins"

    class OUTPUT:
        class GUI:
            ENABLE: str = f"{MUMIMO_CFG_SECTIONS.OUTPUT_GUI}.enable"

            class CANVAS:
                BACKGROUND_COLOR: str = f"{MUMIMO_CFG_SECTIONS.OUTPUT_GUI_CANVAS}.background_color"
                IMAGE_BACKGROUND_COLOR: str = f"{MUMIMO_CFG_SECTIONS.OUTPUT_GUI_CANVAS}.image_background_color"
                CONTENT_ALIGNMENT: str = f"{MUMIMO_CFG_SECTIONS.OUTPUT_GUI_CANVAS}.content_alignment"
                BORDER: str = f"{MUMIMO_CFG_SECTIONS.OUTPUT_GUI_CANVAS}.border"

            class TEXT:
                FONT: str = f"{MUMIMO_CFG_SECTIONS.OUTPUT_GUI_TEXT}.font"
                STANDARD_TEXT_COLOR: str = f"{MUMIMO_CFG_SECTIONS.OUTPUT_GUI_TEXT}.standard_text_color"
                HEADER_TEXT_COLOR: str = f"{MUMIMO_CFG_SECTIONS.OUTPUT_GUI_TEXT}.header_text_color"
                SUB_HEADER_TEXT_COLOR: str = f"{MUMIMO_CFG_SECTIONS.OUTPUT_GUI_TEXT}.sub_header_text_color"
                INDEX_TEXT_COLOR: str = f"{MUMIMO_CFG_SECTIONS.OUTPUT_GUI_TEXT}.index_text_Color"
