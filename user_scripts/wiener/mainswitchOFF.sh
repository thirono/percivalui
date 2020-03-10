#!/bin/bash

# Switch the WIENER OFF

echo Switching the WIENER Power Supply OFF

# read -n1 -rsp $'Press any key to continue or Ctrl+C to exit...\n'

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru 169.254.1.240 sysMainSwitch.0 i 0
