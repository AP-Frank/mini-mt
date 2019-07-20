#!/bin/bash

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$THIS_DIR"

# install tools if neccessary
sudo apt update
sudo apt install dnsmasq hostapd

sudo systemctl stop dnsmasq
sudo systemctl stop hostapd

# set up dhcp
sudo mv /etc/dhcpcd.conf /etc/dhcpcd.conf.orig
sudo cp dhcpcd.conf /etc/

sudo service dhcpcd restart

sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
sudo cp dnsmasq.conf /etc/

sudo service dnsmasq restart

# set up access point
sudo cp hostapd.conf /etc/hostapd/hostapd.conf
sudo cp hostapd /etc/default/hostapd

sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl start hostapd

sudo cp sysctl.conf /etc
sudo iptables -t nat -A  POSTROUTING -o eth0 -j MASQUERADE
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"

sudo cp /etc/rc.local /etc/rc.local.orig
sudo sed -i "s,exit 0,iptables-restore < /etc/iptables.ipv4.nat\nexit 0,g" /etc/rc.local

