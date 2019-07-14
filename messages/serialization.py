from typing import Union

from message_types import MessageType
from command_message import CommandMessage
from time_message import TimeMessage
from string_message import StringMessage


def from_bytes(bb: bytes) -> Union[CommandMessage, TimeMessage, StringMessage]:
    """
    Extracts all known messages
    """
    message_type = int.from_bytes(bb[0:1], byteorder='Big', signed=False)

    if message_type == MessageType.TIME_MESSAGE:
        return TimeMessage.from_bytes(bb)
    elif message_type == MessageType.COMMAND_MESSAGE:
        return CommandMessage.from_bytes(bb)
    elif message_type == MessageType.STRING_MESSAGE:
        return StringMessage.from_bytes(bb)
    else:
        raise Exception("Unknown message type: " + str(message_type))
