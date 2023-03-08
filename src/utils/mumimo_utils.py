import platform
from typing import List, Optional


def is_supported_platform() -> bool:
    return platform.system() in ("Linux", "Darwin")


def parse_channel_tokens(tokens: str) -> Optional[List[str]]:
    if not isinstance(tokens, str):
        return None
    tokens = tokens.strip()
    if not tokens:
        return None
    tokens = " ".join(tokens.split())
    return [token.strip() for token in tokens.split()]
