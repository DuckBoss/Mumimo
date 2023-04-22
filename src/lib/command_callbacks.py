from typing import Any, Callable, Dict, List, Optional, Tuple


class CommandCallbacks(Dict[str, Dict[str, Any]]):
    def register_command(
        self,
        callback_name: str,
        plugin_name: str,
        command_func: Callable,
        command_parameters: Optional[List[str]] = None,
        parameters_required: bool = False,
        exclusive_parameters: Optional[List[str]] = None,
    ) -> Dict[str, Dict[str, Any]]:
        if self.get(callback_name) is None:
            self[callback_name] = {}
        if command_parameters is None:
            command_parameters = []
        if exclusive_parameters is None:
            exclusive_parameters = []
        self[callback_name] = {
            "command": callback_name,
            "func": command_func,
            "plugin": plugin_name,
            "parameters": command_parameters,
            "parameters_required": parameters_required,
            "exclusive_parameters": exclusive_parameters,
        }
        return self

    def remove_command(self, callback_name: str) -> bool:
        try:
            del self[callback_name]
            return True
        except KeyError:
            return False

    def unregister_command(self, callback_name: str) -> bool:
        return self.remove_command(callback_name)

    def unregister_plugin(self, plugin_name: str) -> Tuple[bool, Dict[str, Dict[str, Any]]]:
        to_delete = []
        failed_unregisters = {}
        success_unregisters = {}
        for name, callback in self.items():
            if callback["plugin"] == plugin_name:
                to_delete.append((name, callback))
        for name, callback in to_delete:
            _attempt = self.unregister_command(name)
            if not _attempt:
                failed_unregisters[name] = callback
            else:
                success_unregisters[name] = callback
        if failed_unregisters:
            return (False, failed_unregisters)
        return (True, success_unregisters)

    def get_exclusive_parameters(self, callback_name: str) -> List[str]:
        callback: Optional[Dict[str, Any]] = self.get(callback_name, None)
        if callback is None:
            return []
        parameters: List[str] = callback.get("exclusive_parameters", [])
        return parameters

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
