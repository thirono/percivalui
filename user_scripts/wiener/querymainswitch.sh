#!/bin/bash

WIENER_IP=172.23.16.179

snmpget -v 2c -m +WIENER-CRATE-MIB -c public $WIENER_IP sysMainSwitch.0
