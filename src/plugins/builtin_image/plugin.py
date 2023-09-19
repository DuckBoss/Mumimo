import logging
from typing import TYPE_CHECKING, List, Optional

from pymumble_py3.channels import Channel
from pymumble_py3.users import User

from src.constants import LogOutputIdentifiers
from src.lib.frameworks.plugins.plugin import PluginBase
from src.settings import settings
from src.utils import mumble_utils
from src.lib.frameworks.gui.gui import GUIFramework
from .utility.constants import ParameterDefinitions

logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from src.lib.command import Command


class Plugin(PluginBase):
    command = PluginBase.makeCommandRegister()

    def __init__(self, plugin_name: str) -> None:
        self._plugin_name = plugin_name
        logger.debug(f"[{LogOutputIdentifiers.PLUGINS}]: Initializing plugin: '{self._plugin_name}'")
        super().__init__(self._plugin_name)

        self.initialize_parameters(settings.commands.callbacks.get_callbacks(self._plugin_name))
        logger.debug(f"[{LogOutputIdentifiers.PLUGINS}]: Plugin '{self._plugin_name}' ready.")

    @command(
        parameters=ParameterDefinitions.Image.get_definitions(),
    )
    def image(self, data: "Command") -> None:
        # Example:
        # !image "image.jpg"  -> Without a target parameter, by default posts the specified image in the bot channel.
        #
        # Filter types:
        # !image.grayscale "image.jpg"  -> Posts the specified image with a grayscale filter applied.
        # !image.invert "image.jpg"  -> Posts the specified image with an invert filter applied.
        # !image.rotate=90 "image.jpg"  -> Posts the specified image with a rotate filter applied with the specified rotation degrees.
        # !image.compress=50 "image.jpg"  -> Posts the specified image with a compress filter applied with the specified compression ratio.
        # !image.brightness=50 "image.jpg"  -> Posts the specified image with a brightness filter applied with the specified brightness amount.
        # !image.contrast=50 "image.jpg"  -> Posts the specified image with a brightness filter applied with the specified contrast amount.
        #
        # Display types:
        # !image.channel="channel_name" "image.jpg"  -> Posts the specified image in the specified channel.
        # !image.channels="channel1,channel2" "image.jpg"  -> Posts the specified image in the specified channels.
        # !image.user="user_name" "image.jpg"  -> Posts the specified image to the specified user.
        # !image.users="user1,user2" "image.jpg"  -> Posts the specified image to the specified users.
        # !image.broadcast "image.jpg"  -> Posts the specified image to all channels.

        _parameters = self.verify_parameters(self.image.__name__, data)
        if _parameters is None:
            return

    # Filter parameters:
    def _parameter_image_grayscale(self, data: "Command", parameter: str) -> None:
        pass

    def _parameter_image_invert(self, data: "Command", parameter: str) -> None:
        pass

    def _parameter_image_rotate(self, data: "Command", parameter: str) -> None:
        pass

    def _parameter_image_compress(self, data: "Command", parameter: str) -> None:
        pass

    def _parameter_image_brightness(self, data: "Command", parameter: str) -> None:
        pass

    def _parameter_image_contrast(self, data: "Command", parameter: str) -> None:
        pass

    # Display type parameters:
    def _parameter_image_me(self, data: "Command", parameter: str) -> bool:
        return True

    def _parameter_image_broadcast(self, data: "Command", parameter: str) -> None:
        _all_channels: List["Channel"] = mumble_utils.get_all_channels()
        if not _all_channels:
            logger.error(f"[{LogOutputIdentifiers.PLUGINS_COMMANDS}]: '{data.command}' command error: the channel tree could not be retrieved.")
            return
        GUIFramework.gui(
            data.message,
            target_channels=_all_channels,
            user_id=data.actor,
        )

    def _parameter_image_user(self, data: "Command", parameter: str) -> Optional["User"]:
        return self._get_user(data, parameter)

    def _parameter_image_users(self, data: "Command", parameter: str) -> Optional[List["User"]]:
        parameter_split = parameter.split("=", 1)
        if len(parameter_split) == 2:
            user_names = [user.strip().replace("_", " ") for user in parameter_split[1].split(",")]
            if not user_names:
                GUIFramework.gui(
                    f"'{data._command}' command warning: no users were provided.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                )
                return
            _found_users: List["User"] = []
            for _user in user_names:
                if not _user:
                    continue
                _search_user: Optional["User"] = mumble_utils.get_user_by_name(_user)
                if _search_user is not None:
                    _found_users.append(_search_user)
                    continue
                GUIFramework.gui(
                    f"'{data._command}' command warning: cannot find specified user '{_user}'.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                )
            return _found_users
        GUIFramework.gui(
            f"'{data._command}' command warning: an invalid list of user names was provided.",
            target_users=mumble_utils.get_user_by_id(data.actor),
        )

    def _parameter_image_channel(self, data: "Command", parameter: str) -> Optional["Channel"]:
        return self._get_channel(data, parameter)

    def _parameter_image_channels(self, data: "Command", parameter: str) -> Optional[List["Channel"]]:
        parameter_split = parameter.split("=", 1)
        if len(parameter_split) == 2:
            channel_names = [channel.strip().replace("_", " ") for channel in parameter_split[1].split(",")]
            if not channel_names:
                GUIFramework.gui(
                    f"'{data._command}' command warning: no channel names were provided.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                )
                return
            _found_channels: List["Channel"] = []
            for _channel in channel_names:
                if not _channel:
                    continue
                _search_channel: Optional["Channel"] = mumble_utils.get_channel_by_name(_channel)
                if _search_channel is not None:
                    _found_channels.append(_search_channel)
                    continue
                GUIFramework.gui(
                    f"'{data._command}' command warning: cannot find specified channel '{_channel}'.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                )
            return _found_channels
        GUIFramework.gui(
            f"'{data._command}' command warning: an invalid list of channel names was provided.",
            target_users=mumble_utils.get_user_by_id(data.actor),
        )

    # Utility methods:
    def _get_user(self, data: "Command", parameter: str):
        parameter_split = parameter.split("=", 1)
        if len(parameter_split) == 2:
            _search_term: str = parameter_split[1].strip().replace("_", " ")
            if not _search_term:
                GUIFramework.gui(
                    f"'{data._command}' command warning: an invalid user name was provided.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                )
                return
            _search_user: Optional["User"] = mumble_utils.get_user_by_name(_search_term)
            if _search_user is not None:
                return _search_user
            GUIFramework.gui(
                f"'{data._command}' command warning: cannot find specified user '{_search_term}'.",
                target_users=mumble_utils.get_user_by_id(data.actor),
            )
            return
        GUIFramework.gui(
            f"'{data._command}' command warning: a user name was not provided.",
            target_users=mumble_utils.get_user_by_id(data.actor),
        )

    def _get_channel(self, data: "Command", parameter: str):
        parameter_split = parameter.split("=", 1)
        if len(parameter_split) == 2:
            _search_term: str = parameter_split[1].strip().replace("_", " ")
            if not _search_term:
                GUIFramework.gui(
                    f"'{data._command}' command warning: an invalid channel name was provided.",
                    target_users=mumble_utils.get_user_by_id(data.actor),
                )
                return
            _search_channel: Optional["Channel"] = mumble_utils.get_channel_by_name(_search_term)
            if _search_channel is not None:
                return _search_channel
            GUIFramework.gui(
                f"'{data._command}' command warning: cannot find specified channel '{_search_term}'.",
                target_users=mumble_utils.get_user_by_id(data.actor),
            )
            return
        GUIFramework.gui(
            f"'{data._command}' command warning: a channel name was not provided.",
            target_users=mumble_utils.get_user_by_id(data.actor),
        )
