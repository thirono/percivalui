#!/bin/bash

# Switch the WIENER On

WIENER_IP=172.23.16.179

echo Switching the WIENER Power Supply ON

# read -n1 -rsp $'Press any key to continue or Ctrl+C to exit...\n'

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP sysMainSwitch.0 i 1

echo WIENER Power Supply switched ON
