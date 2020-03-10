#!/bin/bash

# Switch the CarrierBoard Off

# echo Switching the CarrierBoard OFF

# read -n1 -rsp $'Press any key to continue or Ctrl+C to exit...\n'

# sleep 5

#12V_supply

echo Ramping 12V_supply down

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru 169.254.1.240 outputVoltage.u200 F 10

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru 169.254.1.240 outputVoltage.u200 F 8

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru 169.254.1.240 outputVoltage.u200 F 6

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru 169.254.1.240 outputVoltage.u200 F 4

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru 169.254.1.240 outputVoltage.u200 F 2

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru 169.254.1.240 outputVoltage.u200 F 0.001

echo 12V_supply is at 0V

sleep 2

#Switch channel OFF

echo Switching 12V_supply OFF

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru 169.254.1.240 outputSwitch.u200 i 0

sleep 2

echo All channels are OFF

echo CarrierBoard is OFF

# Switch the WIENER Off

# ./mainswitchOFF.sh

