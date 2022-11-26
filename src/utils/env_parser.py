import pathlib
from typing import Dict, Optional

from dotenv import dotenv_values


def get_env_file(file_name: str) -> Optional[pathlib.Path]:
    # Check file path is valid:
    if file_name is None or len(file_name) == 0:
        return None
    # Check if file exists:
    rel_path = pathlib.Path.cwd() / file_name
    if rel_path.is_file():
        return rel_path
    return None


def read_env_file(file_name: str) -> Dict[str, Optional[str]]:
    env_path = get_env_file(file_name)
    if env_path is None:
        raise Exception(f"Could not find environment file at: {file_name}")
    env_vars = dotenv_values(dotenv_path=env_path)
    return env_vars
