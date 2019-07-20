import datetime as dt
import os
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


def main(settings: config.config.Settings) -> None:
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
                settings.airodump_command = msg.string
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


def set_time(time: dt.datetime) -> None:
    time_string = time.isoformat()
    logging.info(f'Adjusting our time to {time_string}')
    subprocess.call(shlex.split(f"sudo date -s {time_string}"))


def start_wlan_measurement(settings: config.config.Settings) -> None:
    output_file = os.path.join(settings.capture_path, 'capture')

    # get wlans, this only works on linux
    network_dir = os.path.join(os.sep, 'sys', 'class', 'net')
    ifaces = os.listdir(network_dir)

    # find names of interfaces which have the correct MAC addresses
    airo_ifaces = []
    for interface in ifaces:
        with open(os.path.join(network_dir, interface, 'address'), 'r') as f:
            # make sure that string is lowercase and free of whitespaces
            mac_actual: str = f.readline().strip().lower()

            for mac_airo in settings.airodump_iface_macs:
                # when the substring that is mac_airo is found at position 0
                # we know that our mac address matches
                if mac_actual.find(mac_airo) == 0:
                    airo_ifaces.append(interface)
                    break

    logging.info(f'Creating output directory {output_file}')
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # set output file and all available interfaces
    call_statement = settings.airodump_command.format(
        wlans=','.join(airo_ifaces), output_file=output_file)
    logging.info(f'Starting Airodump with command:\n\t{call_statement}\n')

    while True:
        print(call_statement)
        proc = subprocess.Popen(shlex.split(
            call_statement), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        time.sleep(settings.cap_freq)
        subprocess.call('sudo killall airodump-ng', shell=True)
