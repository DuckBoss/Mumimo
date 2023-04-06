import logging
import pathlib
from typing import Any, Dict, Union

import toml

from ..exceptions import ServiceError

logger = logging.getLogger(__name__)


def process_metadata(plugin_path: Union[pathlib.Path, str]) -> Dict[str, Any]:
    try:
        path = plugin_path
        if isinstance(plugin_path, pathlib.Path):
            path = str(plugin_path.resolve())
        with open(path, "r", encoding="utf-8") as file_handler:
            contents: Dict[str, Any] = toml.load(file_handler, _dict=dict)
            if contents is None:
                raise ServiceError("Unable to process plugin metadata. Please check the syntax and formatting.", logger=logger)
            return contents
    except IOError as exc:
        raise ServiceError("Unable to process plugin metadata. Metadata file not found.", logger=logger) from exc
