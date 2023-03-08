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


class LOG_CFG_SECTION:
    OUTPUT: str = "output"
    LOGGING: str = "logging"
    CONSOLE: str = "console"


class LOG_CFG_FIELD:
    class OUTPUT:
        class LOGGING:
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


class CFG_SECTION:
    class SETTINGS:
        CONNECTION: str = "settings.connection"
        COMMANDS: str = "settings.commands"
        MEDIA: str = "settings.media"
        MEDIA_AUDIO_DUCKING: str = "settings.media.audio_ducking"
        MEDIA_YOUTUBE_DL: str = "settings.media.youtube_dl"
        PLUGINS: str = "settings.plugins"

    class OUTPUT:
        GUI: str = "output.gui"
        GUI_CANVAS: str = "output.gui.canvas"
        GUI_TEXT: str = "output.gui.text"


class CFG_FIELD:
    class SETTINGS:
        USERNAME: str = "username"
        SUPERUSER: str = "superuser"

        class CONNECTION:
            MUTE: str = "mute"
            DEAFEN: str = "deafen"
            REGISTER: str = "register"
            COMMENT: str = "comment"
            DEFAULT_CHANNEL: str = "default_channel"
            AUTO_RECONNECT: str = "auto_reconnect"

        class COMMANDS:
            TOKEN: str = "command_token"
            TICK_RATE: str = "command_tick_rate"
            MAX_MULTI_COMMAND_LENGTH: str = "max_multi_command_length"
            MAX_COMMAND_QUEUE_LENGTH: str = "max_command_queue_length"
            MESSAGE_HISTORY_LENGTH: str = "message_history_length"

        class MEDIA:
            VOLUME: str = "volume"
            STEREO_AUDIO: str = "stereo_audio"
            MAX_QUEUE_LENGTH: str = "max_queue_length"
            FFMPEG_PATH: str = "ffmpeg_path"
            VLC_PATH: str = "vlc_path"
            MEDIA_DIRECTORY: str = "media_directory"

            class AUDIO_DUCKING:
                ENABLE: str = "enable"
                VOLUME: str = "volume"
                THRESHOLD: str = "threshold"
                DELAY: str = "delay"

            class YOUTUBE_DL:
                PROXY_URL: str = "proxy_url"
                COOKIE_FILE: str = "cookie_file"

        class PLUGINS:
            DISABLED_PLUGINS: str = "disabled_plugins"
            SAFE_MODE_PLUGINS: str = "safe_mode_plugins"

    class OUTPUT:
        class GUI:
            ENABLE: str = "enable"

            class CANVAS:
                BACKGROUND_COLOR: str = "background_color"
                IMAGE_BACKGROUND_COLOR: str = "image_background_color"
                CONTENT_ALIGNMENT: str = "content_alignment"
                BORDER: str = "border"

            class TEXT:
                FONT: str = "Georgia"
                STANDARD_TEXT_COLOR: str = "standard_text_color"
                HEADER_TEXT_COLOR: str = "header_text_color"
                SUB_HEADER_TEXT_COLOR: str = "sub_header_text_color"
                INDEX_TEXT_COLOR: str = "index_text_Color"
