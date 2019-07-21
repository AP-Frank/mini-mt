import configparser
import sys


class Settings:

    def __init__(self, path):
        self.read_config(path)

    def read_config(self, path):
        config = configparser.ConfigParser()
        config.read(path)

        try:
            general_config = config['general']
            network_config = config['network']
            timer_config = config['timers']
            airodump_config = config['airodump']
            storage_config = config['storage']

            self.isServer = general_config['Profile'].lower() == 'server'
            self.log_level = general_config['LoggingLevel'].upper()
            if self.log_level not in ['ERROR', 'WARNING', 'INFO', 'DEBUG']:
                raise Exception(f"config.ini: LoggingLevel {self.log_level} is invalid")
            
            # network config
            self.server_ip = network_config['ServerIP']
            self.server_port = network_config.getint('ServerPort')

            # timer config
            self.cap_freq = timer_config.getint('CaptureFrequency')
            self.select_timeout = timer_config.getint('SelectTimeout')

            # storage config
            self.zip = storage_config.getboolean('ZipCaptures')
            self.zip_freq = storage_config.getint('ZipFreq')
            self.zip_file_buffer = storage_config.getint('FileBuffer')
            if self.zip_file_buffer < 1:
                raise Exception(f"config.ini: FileBuffer {self.log_level} must be at least 1")
            self.zip_path = storage_config['StoragePath']
            self.zip_group_size = storage_config.getint('GroupSize')

            # airodump config
            self.airodump_command = airodump_config['Command']
            ifaces = airodump_config['InterfaceMACs']
            self.airodump_iface_macs = [x.strip().lower() for x in ifaces.split(',')]
            self.capture_path = airodump_config['CapturePath']

            
        except KeyError as ex:
            print("Config misses entry for:" + ex.args[0])
            sys.exit(2)
