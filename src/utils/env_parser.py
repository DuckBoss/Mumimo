import pathlib
from typing import Dict, Optional

from dotenv import dotenv_values


def get_env_file(file_name: str) -> Optional[pathlib.Path]:
    # Check for file in cwd:
    env_path = pathlib.Path.cwd() / file_name
    if env_path.is_file():
        return env_path
    # Check for absolute path:
    env_path = pathlib.Path(file_name)
    if env_path.is_file():
        return env_path
    return None


def read_env_file(file_name: str) -> Dict[str, Optional[str]]:
    env_path = get_env_file(file_name)
    if env_path is None:
        raise Exception(f"Could not find environment file at: {env_path}")
    env_vars = dotenv_values(dotenv_path=env_path)
    return env_vars
