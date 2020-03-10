#!/bin/bash

snmpget -v 2c -m +WIENER-CRATE-MIB -c public 169.254.1.240 sysMainSwitch.0
