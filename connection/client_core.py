import datetime as dt
import logging
import shlex
import socket
import subprocess
import time

import config.config
from connection.socket_wrapper import SocketWrapper
from messages.command_message import CommandMessage
from messages.message_types import Command
from messages.string_message import StringMessage
from messages.time_message import TimeMessage


def main(settings: config.config.Settings):
    while(True):
        try:
            logging.info('Trying to connect to server')
            sock = socket.create_connection(
                (settings.server_ip, int(settings.server_port)))
            wsock = SocketWrapper(sock, settings.select_timeout)

            msg = wsock.receive_message()
            if isinstance(msg, TimeMessage):
                set_time(msg.datetime)
            else:
                # first message has to be time
                continue

            msg = wsock.receive_message()
            if not isinstance(msg, CommandMessage) or msg.command != Command.COMMAND:
                # we expect a the airodump command next
                continue

            msg = wsock.receive_message()
            if isinstance(msg, StringMessage):
                # set the actual airodump command
                settings.airodump_command = msg.command
            else:
                continue

            msg = wsock.receive_message()
            if isinstance(msg, CommandMessage):
                if msg.command == Command.START:
                    wsock.send_message(bytes(CommandMessage(Command.CYA)))
                    sock.close()
                    break

        except socket.timeout:
            logging.info('Socket connect has timed out, restarting')
            pass

    start_wlan_measurement(settings)


def set_time(time: dt.datetime):
    time_string = time.isoformat()
    logging.info(f'Adjusting our time to {time_string}')
    subprocess.call(shlex.split(f"sudo date -s {time_string}"))


def start_wlan_measurement(settings: config.config.Settings):
    output_file = "{}/capture".format(settings.capture_path)
    call_statement = settings.airodump_command.format(output_file=output_file)
    logging.info(f'Starting Airodump with command:\n\t{call_statement}\n')
    
    while True:     
        print(call_statement)
        proc = subprocess.Popen(shlex.split(call_statement), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        time.sleep(settings.cap_freq)
        subprocess.call('sudo killall airodump-ng', shell=True)
