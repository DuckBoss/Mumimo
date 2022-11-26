import re

VERSION: str = "0.0.1"


def version():
    return VERSION


def validate_version() -> bool:
    return re.fullmatch(r"\d{1,3}.\d{1,3}.\d{1,3}", version()) is not None
