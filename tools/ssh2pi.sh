#!/bin/bash

MSG_ERROR='[\e[31mERROR\e[0m]'

LOC=$(basename $0)

function print_help {
    echo "Connect to other Pis or list available Pis"
    echo "Usage:"
    echo ""
    echo -e "\t./$LOC <host>"
    echo ""
    echo "Arguments:"
    echo -e "\thost : Address or Hostname of the target"
    echo "Options:"
    echo -e "\t-h : Display this help message"
    echo -e "\t-l : List devices in this subnet"
}


while getopts ":hl" opt; do
    case $opt in
        h)
            print_help
            exit 0
            ;;
        l)
            sudo arp-scan --interface=wlan0 --localnet --ignoredups
			exit 0
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            exit 1
            ;;
        :)
            echo "Option -$OPTARG requires an argument." >&2
            exit 1
            ;;
    esac
done

if [ $# -ne 1 ]; then
    printf "$MSG_ERROR Argument <host> is not specified.\n\n" 1>&2
    print_help
    exit 1
fi

ssh -i ~/keys/mini-mt-piLinux.ppk $1
