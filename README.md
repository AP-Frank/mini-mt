# Mini-MT

This is a simplified version of the MobilityTracking project. The code is completely rewritten to provide more stability, but lacks some of the features of the full project. See also the feature matrix.

## Feature Matrix

| Feature                           | MobilityTracking | Mini-MT |
| --------------------------------- | ---------------- | ------- |
| Unlimited Pis                     | no               | yes     |
| Visualization                     | yes              | no      |
| OEX                               | yes              | no      |
| GUI                               | yes              | no      |
| Pi Management Tools               | no               | yes     |
| Interface Detection               | no               | yes     |
| Airodump Output in Intervals      | yes              | yes     |
| Compression of Output             | yes              | yes     |
| Autostart with old Configurations | no               | yes     |


## Usage
**Note:** If the project is not set up, follow the setup notes first.

Adapt the settings on the clients and the server according to your preferences (edit ``config/config.ini``). Clients are set up to automatically connect to the server on startup.

On the server navigate to the directory where this repository resides. Then type:
````bash
pipenv shell
python main.py

# or
pipenv run python main.py
````

## Setup Notes
The setup of a Raspberry Pi is automated as far as possible without to much effort. Target: Pi 3 with Raspbian OS. When setting up a new Pi follow these instructions (**Note**: Internet access is required):

1. Setup SSH
   
    Enable SSH on the Pi. Create an SSH key and deploy them in a folder ``/home/pi/keys/``. Add the public key to the ``.ssh/authorized_keys`` file. **Note:** The user which executes the program needs ``sudo`` privileges without a password. ``sudo`` must be installed.

2. Clone the Repository

    ````bash
    git clone https://github.com/AP-Frank/mini-mt.git
    ````

3. Install Python 3.7

    If Python 3.7 is available on the system skip this step. Otherwise execute ``install.sh``.

4. Activate Predictable Interface Names

    If already activated skip this step. Otherwise run ``raspi-config``, select ``Network Options -> Network Interface Names`` and enable this option.

5. Remaining configuration

    The directory ``rasp-setup`` contains scripts to setup either a client or a server. The configuration files which are set are also contained in this directory.

    - On a server, prior to executing ``setup-server.sh`` you **should** change the ``hostapd.conf`` file to specify a different network name and password. If you want to change the servers IP address edit ``dhcpcd.conf``. You should then also adapt the IP ranges which are given out by our local DHCP server in ``dnsmasq.conf``.

    - On a client, prior to executing ``setup-client.sh`` you **should** change the ``wpa_supplicant.conf`` file to also specify your network name and password.

    The remaining configuration of the Pi is done within the ``config/config.ini`` file. All options are explained within this file.

## Program Purpose
The main purpose of this project is to have a simple system to instruct Raspberry Pis to conduct long running airodump measurements. One Pi acts as a server, it creates an access point to which the clients connect (a user may also use the access point to control this Pi). The user can set an airodump command in the configuration file of the server, this command will be sent to all client which connect.

For airodump measurements the client should have at least one external antenna, the internal one is used to communicate with the server. After booting a client will immediately start measuring if it finds an airodump command from the previous run. In any case it will try to connect to the server Pi and fetch a new command. If the connection is successful it will use the new command to capture packets, otherwise it will continue with the old command.

A typical use case might look like this:
1. Configure the client Pis via the server
2. Place the clients at the locations they are supposed to measure at
3. Clients can be turned on and off (whenever powered on they will continue measuring)
4. Come back later with the server Pi. Clients automatically connect to its AP and you can ssh/scp your measured files from the clients

## Design Choices
- *Predictable Interface Names*
    
    While normal interface names are often easier to read, they pose a problem if a Pi uses several antenna which are connected externally. Wlan0 will not always be the internal interface but may in fact refer to any interface, depending on what happened during boot. We always want to use the internal Wifi to connect to other Pis so we need to make sure that this interface has always the same name. Predictable Interface Names is probably the easiest way to make sure that this is the case.

    In any case the user does not need to worry about the interface names as the Pis discover antenna by MAC address.

- *Old Configuration Autostart*

    When a client is started, it detects if a configuration (aka an airodump command) from a previous run is found. In that case it immediately executes this command, and after that will try to contact the server to fetch a new configuration. If that fails it will keep running the old command.

    Currently only the airodump command from the previous configuration is used, all other settings (e.g., the servers IP address) are drawn from the current configuration file of the client.


       