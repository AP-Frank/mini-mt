#!/bin/bash

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$THIS_DIR"

mkdir -p backups

sudo apt update
sudo apt install arp-scan

sudo cp /etc/wpa_supplicant/wpa_supplicant.conf backups/wpa_supplicant.conf.orig
sudo cp wpa_supplicant.conf /etc/wpa_supplicant/

# this makes sure that only wlan0 is configured by dhcp, the rest is ignore
# https://serverfault.com/a/880575
sudo cp /lib/dhcpcd/dhcpcd-hooks/10-wpa_supplicant backups/10-wpa_supplicant.orig
sudo sed -i 's,if \[ "\$ifwireless" = "1" \] \&\& \\,if \[ "\$ifwireless" = "1" \] \&\& \[ "\$interface" = "wlan0" \] \&\& \\,g' /lib/dhcpcd/dhcpcd-hooks/10-wpa_supplicant
