from messages.message_types import Command, MessageType


class CommandMessage:
    """
    Message which contains a single command

    Commands are used to signal/trigger certain events, they do not
    contain data apart from their type
    """

    def __init__(self, command: Command):
        self.command = command

    def __bytes__(self):
        type_buf = MessageType.COMMAND_MESSAGE.to_bytes(
            1, byteorder='Big', signed=False)
        command_buf = self.command.to_bytes(1, byteorder='Big', signed=False)
        return type_buf + command_buf

    @staticmethod
    def from_bytes(bb: bytes):
        msg_type = int.from_bytes(bb[0:1], byteorder='Big', signed=False)
        assert msg_type == MessageType.COMMAND_MESSAGE
        assert len(bb) == 2

        command = Command(int.from_bytes(
            bb[1:2], byteorder='Big', signed=False))
        return CommandMessage(command)
