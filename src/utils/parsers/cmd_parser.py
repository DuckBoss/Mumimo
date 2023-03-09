from typing import List, Optional, TYPE_CHECKING

from ...config import Config
from ...constants import MumimoCfgFields
from ...corelib.command import Command

if TYPE_CHECKING:
    from pymumble_py3.mumble import Mumble


def parse_command(text, _cfg_instance: Config) -> Optional[Command]:
    if not text:
        return None
    message = text.message
    if not message:
        return None

    actor = text.actor
    channel_id = text.channel_id
    if channel_id:
        channel_id = channel_id[0]
    session_id = text.session
    if session_id:
        session_id = session_id[0]
    message = message.strip()
    if not message:
        return None

    if message[0] != _cfg_instance.get(MumimoCfgFields.SETTINGS.COMMANDS.TOKEN, "!"):
        return Command(message=message, actor=actor, channel_id=channel_id, session_id=session_id)

    text_parse_list: List[str] = message.split(" ", 1)
    cmd_parse_list = text_parse_list[0].split(".", 1)

    cmd = cmd_parse_list[0][1:]
    if not cmd:
        cmd = None

    try:
        parameters = cmd_parse_list[1].split(".")
        parameters = [opt for opt in parameters if opt]
    except IndexError:
        parameters = None

    try:
        message_body = text_parse_list[1]
    except IndexError:
        message_body = ""

    return Command(command=cmd, parameters=parameters, message=message_body, actor=actor, channel_id=channel_id, session_id=session_id)


def parse_actor_name(command: "Command", connection_instance: "Mumble") -> str:
    try:
        actor_name: Optional[str] = connection_instance.users[command.actor]["name"]
    except KeyError:
        actor_name = "Server"
    if actor_name is None:
        actor_name = "Unavailable"
    return actor_name


def parse_channel_name(command: "Command", connection_instance: "Mumble") -> str:
    try:
        channel_name: Optional[str] = connection_instance.channels[command.channel_id]["name"]
    except Exception:  # protobuf error raised here if the channel_id does not exist.
        channel_name = "Server"
        if command.is_private:
            channel_name = "Private"
    if channel_name is None:
        channel_name = "Unavailable"
    return channel_name


def parse_message_image_data(command: "Command") -> str:
    if "<img" in command.message:
        message = "Image Data"
    else:
        message = command.message
    return message


def parse_message_hyperlink_data(command: "Command") -> str:
    if "<a href=" in command.message:
        message = "Hyperlink Data"
    else:
        message = command.message
    return message
