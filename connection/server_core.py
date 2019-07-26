import socket
import logging
from threading import Thread

from config.config import Settings
from messages.command_message import CommandMessage
from messages.message_types import Command
from messages.time_message import TimeMessage
from messages.string_message import StringMessage
from connection.socket_wrapper import SocketWrapper


def main(settings: Settings) -> None:
    # we set the default timeout, it should be inherited by sockets
    # created via accept
    socket.setdefaulttimeout(settings.socket_timeout)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_port = settings.server_port

    # Allow rebinding of same address when restarting the server
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind(("", server_port))
    server_socket.listen(5)

    while True:
        try:
            logging.info('Waiting for client connections')
            (client_socket, address) = server_socket.accept()
            t = Thread(target=run, args=(client_socket, address, settings))
            t.start()
        except socket.timeout:
            logging.warn('Socket accept has timed out, restarting ...')
            pass


def run(client_socket: socket.socket, address: (str, int), settings: Settings) -> None:
    """
    Thread which handles one client connection
    """
    logging.info(f'Client (ip: {address[0]}) has connected')
    wsock = SocketWrapper(client_socket)

    while(True):
        # now send timestamp and start signal
        logging.info('Starting to send data')
        wsock.send_message(bytes(TimeMessage()))
        wsock.send_message(bytes(CommandMessage(Command.COMMAND)))
        wsock.send_message(bytes(StringMessage(settings.airodump_command)))
        wsock.send_message(bytes(CommandMessage(Command.START)))

        msg = wsock.receive_message()
        if isinstance(msg, CommandMessage):
            if msg.command == Command.CYA:
                logging.info('Client has signaled successfull start of operation')
                # remote device has started successfully
                break

        # TODO: maybe add some additional error handling here


