import platform


def is_supported_platform() -> bool:
    return platform.system() in ("Linux", "Darwin")
