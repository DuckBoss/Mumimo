from typing import Any, Callable, Dict, List, Optional


class CommandCallbacks(Dict[str, Dict[str, Any]]):
    def register_command(
        self,
        callback_name: str,
        plugin_name: str,
        command_func: Callable,
        command_parameters: Optional[List[str]],
        parameters_required: bool = False,
    ) -> Dict[str, Dict[str, Any]]:
        if self.get(callback_name) is None:
            self[callback_name] = {}
        if command_parameters is None:
            command_parameters = []
        self[callback_name] = {
            "command": callback_name,
            "func": command_func,
            "plugin": plugin_name,
            "parameters": command_parameters,
            "parameters_required": parameters_required,
        }
        return self

    def remove_command(self, callback_name: str) -> bool:
        try:
            del self[callback_name]
            return True
        except KeyError:
            return False

    def get_parameters_required(self, callback_name: str) -> bool:
        callback: Optional[Dict[str, Any]] = self.get(callback_name, None)
        if callback is None:
            return False
        return callback.get("parameters_required", False)

    def get_command_parameters(self, callback_name: str) -> List[str]:
        callback: Optional[Dict[str, Any]] = self.get(callback_name, None)
        if callback is None:
            return []
        parameters: List[str] = callback.get("parameters", [])
        return parameters

    def get_command(self, callback_name: str) -> Optional[Callable]:
        callback: Optional[Dict[str, Any]] = self.get(callback_name, None)
        if callback is None:
            return None
        command_func: Optional[Callable] = callback.get("func", None)
        return command_func

    def get_plugin(self, callback_name: str) -> Optional[str]:
        callback: Optional[Dict[str, Any]] = self.get(callback_name, None)
        if callback is None:
            return None
        plugin_name: Optional[Callable] = callback.get("plugin", None)
        return plugin_name

    def get_callback(self, callback_name: str) -> Optional[Dict[str, Any]]:
        return self.get(callback_name, None)
