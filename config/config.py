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
            path_config = config['paths']
            timer_config = config['timers']
            airodump_config = config['airodump']

            self.isServer = general_config['Profil'].lower() == 'Server'
            
            self.server_ip = network_config['ServerIP']
            self.server_port = network_config['ServerPort']

            self.capture_path = path_config['CapturePath']

            self.cap_freq = timer_config.getint('CaptureFrequency')
            self.sanity_freq = timer_config.getint('SanityCheckFrequency')
            self.del_files_older = timer_config.getint('DeleteFilesOlder')
            self.select_timeout = timer_config.getint('SelectTimeout')

            self.airodump_command = airodump_config['Command']

            
        except KeyError as ex:
            print("Config misses entry for:" + ex.args[0])
            sys.exit(2)
