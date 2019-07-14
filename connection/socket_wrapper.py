import select
import socket

from messages import serialization
from mtexceptions.network_exceptions import ConnectionLost

LENGTH = 1  # size in bytes of the length field


class SocketWrapper:
    """
    Wraps a socket and makes sending and receiving messages easier

    Before sending a message, the socket adds the length of the message
    at the front, so that a message can be received completely. This
    length field is stripped before further processing.

    Effective message layout (with length in bytes)

    [Length : LENGTH][Message : N]
    """
    sock: socket.socket
    do_compress: bool
    select_timeout: float

    def __init__(self, _socket: socket.socket, select_timeout: float):
        self.sock = _socket
        self.select_timeout = select_timeout

    def _send(self, msg: bytes) -> int:
        totalsent = 0
        while totalsent < len(msg):
            # noinspection PyTypeChecker
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                self.sock.close()
                raise ConnectionLost("Connection was lost")
            totalsent = totalsent + sent
        return totalsent

    def _receive(self, nr_bytes: int) -> bytes:
        chunks = []
        bytes_recd = 0
        while bytes_recd < nr_bytes:
            chunk = self.sock.recv(nr_bytes - bytes_recd)
            if chunk == b'':
                self.sock.close()
                raise ConnectionLost("Connection was lost")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        # noinspection PyTypeChecker
        return b''.join(chunks)

    def send_message(self, buf: bytes):
        # prepend the length of the message
        length: int = len(buf)
        len_buf = length.to_bytes(LENGTH, byteorder='Big', signed=False)
        self._send(len_buf + buf)

    def receive_message(self):
        # fetch length header first
        buf = self._receive(LENGTH)
        length = int.from_bytes(buf, byteorder='Big', signed=False)

        # get payload
        buf = self._receive(length)
        return serialization.from_bytes(buf)

    def check_for_incoming_data(self):
        return select.select([self.sock], [], [], self.select_timeout)[0]
