import datetime as dt
import logging
import os
import shlex
import socket
import subprocess
import threading
import time
from typing import Optional

import config.config
import util.save_files as sf
from connection.socket_wrapper import SocketWrapper
from messages.command_message import CommandMessage
from messages.message_types import Command
from messages.string_message import StringMessage
from messages.time_message import TimeMessage

# file where we store saved data
save_path = os.path.join('config', 'save.json')


def main(settings: config.config.Settings) -> None:
    wlan_thread_stop = threading.Event()

    if settings.zip:
        # if set, we just run this infinitely
        zip_thread = threading.Thread(
            target=sf.zip_and_delete, args=(settings,))
        zip_thread.daemon = True
        zip_thread.start()

    try:
        # if succeeds, we have an old configuration available
        loaded_settings = sf.load_data(save_path)

        logging.info('Found config file from previous run')
        wlan_thread = threading.Thread(target=start_wlan_measurement, args=(
            settings, wlan_thread_stop, loaded_settings['airodump_command']))
        wlan_thread.daemon = True
        wlan_thread.start()

        # see if we still can get an updated variant
        contact_successful = contact_server(settings, settings.connection_attempts)
    except FileNotFoundError:
        # we have nothing else to do, we block until
        # we get a connection
        contact_successful = contact_server(settings, None)

    if contact_successful:
        wlan_thread_stop.set()

        logging.info('Successfully fetched new config from server (re-)starting Airodump')

        # lets leave the event from the other thread alone in case
        # it takes a bit longer to stop itself
        wlan_thread_stop = threading.Event()

        # this time run it in the main thread, stop will not be called
        # -> blocking
        start_wlan_measurement(settings, wlan_thread_stop)
    else:
        # this can only happen if we had no previous configuration,
        # in that case just keep running the old config thread
        while(True):
            time.sleep(10)


def contact_server(settings: config.config.Settings, attempts: Optional[int]) -> bool:
    """
    Try to contact the server and get a new configuration (i.e., an airodump command)

    If attempts is greater 0, this is the number of connection attempts conducted. Values of 0
    or lower mean there is no attempt made. None means that infinite attempts are made

    Returns True if a successful connection attempt was made, False otherwise
    """
    connection_successful = False
    print(attempts)

    while(attempts is None or attempts > 0):
        try:
            logging.info('Trying to connect to server.')
            sock = socket.create_connection(
                (settings.server_ip, int(settings.server_port)), timeout=settings.socket_timeout)
            wsock = SocketWrapper(sock)

            msg = wsock.receive_message()
            if isinstance(msg, TimeMessage):
                set_time(msg.datetime)
            else:
                # first message has to be time
                continue

            msg = wsock.receive_message()
            if not isinstance(msg, CommandMessage) or not msg.command == Command.COMMAND:
                # we expect a the airodump command next
                continue

            msg = wsock.receive_message()
            if isinstance(msg, StringMessage):
                # set the actual airodump command
                settings.airodump_command = msg.string
                sf.save_data(vars(settings), save_path)
            else:
                continue

            msg = wsock.receive_message()
            if isinstance(msg, CommandMessage):
                if msg.command == Command.START:
                    wsock.send_message(bytes(CommandMessage(Command.CYA)))
                    connection_successful = True
                    break

        except ConnectionRefusedError:
            logging.info('Server refused connection')
            logging.info('Will retry in 10 seconds')
            time.sleep(10)
        except socket.timeout:
            logging.info('Socket connect has timed out, restarting')
            sock.close()
        finally:
            if isinstance(attempts, int):
                attempts -= 1
                logging.info(f'Remaing attempts {attempts}')

    return connection_successful


def set_time(time: dt.datetime) -> None:
    time_string = time.isoformat()
    logging.info(f'Adjusting our time to {time_string}')
    subprocess.call(shlex.split(f"sudo date -s {time_string}"))


def start_wlan_measurement(settings: config.config.Settings, stop_event: threading.Event, override_command=None) -> None:
    # make sure no other airodump instances are running
    subprocess.call('sudo killall airodump-ng', shell=True)

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
    if override_command is None:
        call_statement = settings.airodump_command.format(
            wlans=','.join(airo_ifaces), output_file=output_file)
    else:
        call_statement = override_command.format(
            wlans=','.join(airo_ifaces), output_file=output_file)
    logging.info(f'Starting Airodump with command:\n\t{call_statement}\n')

    while not stop_event.is_set():
        print(call_statement)
        subprocess.Popen(shlex.split(
            call_statement), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        stop_event.wait(timeout=settings.cap_freq)
        subprocess.call('sudo killall airodump-ng', shell=True)
