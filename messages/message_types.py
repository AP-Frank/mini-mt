from enum import IntEnum


class MessageType(IntEnum):
    TIME_MESSAGE = 0,
    COMMAND_MESSAGE = 1,
    STRING_MESSAGE = 2,


class Command(IntEnum):
    # indicate to client that it should begin operation
    START = 0,

    # indicate to server that operation has been started
    # and connection can be closed
    CYA = 1,

    # following this message is a StringMessage
    # containing a string which should be locally
    # executed
    COMMAND = 2,
