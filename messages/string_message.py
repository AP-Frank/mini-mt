from message_types import MessageType


class StringMessage:
    """
    Message which contains a string
    """

    def __init__(self, string: str):
        self.string = string

    def __bytes__(self):
        string_buf = self.string.encode('UTF-8')
        type_buf = MessageType.STRING_MESSAGE.to_bytes(
            1, byteorder='Big', signed=False)

        return type_buf + string_buf

    @staticmethod
    def from_bytes(bb: bytes) -> 'StringMessage':
        msg_type = int.from_bytes(bb[0:1], byteorder='Big', signed=False)
        assert msg_type == MessageType.STRING_MESSAGE

        string = bb[1:].decode('UTF-8')

        return StringMessage(string)
