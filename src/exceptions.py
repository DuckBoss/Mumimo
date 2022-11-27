class ValidationError(Exception):
    pass


class ConfigError(Exception):
    pass


class ConfigReadError(ConfigError):
    pass


class ConfigWriteError(ConfigError):
    pass
