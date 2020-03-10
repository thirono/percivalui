#!/bin/bash

# Switch the WIENER OFF

WIENER_IP=172.23.16.179

echo Switching the WIENER Power Supply OFF

# read -n1 -rsp $'Press any key to continue or Ctrl+C to exit...\n'

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP sysMainSwitch.0 i 0
