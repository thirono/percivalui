#!/bin/bash

# Switch the WIENER ON

# ./mainswitchON.sh

# Switch the CarrierBoard On

# echo Switching the CarrierBoard ON

# sleep 5

# Set all values to 0 V and current limits

echo Setting current limit and voltage to 0

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru 169.254.1.240 outputVoltage.u200 F 0
snmpset -v 2c -m +WIENER-CRATE-MIB -c guru 169.254.1.240 outputCurrent.u200 F 6

echo All channels set propertly 

sleep 2

#Switch everything ON

echo Switching channel ON

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru 169.254.1.240 outputSwitch.u200 i 1

echo All channels switched ON

sleep 2

#Set the values

#12V_supply

echo Ramping 12V_supply up

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru 169.254.1.240 outputVoltage.u200 F 2

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru 169.254.1.240 outputVoltage.u200 F 4

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru 169.254.1.240 outputVoltage.u200 F 6

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru 169.254.1.240 outputVoltage.u200 F 8

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru 169.254.1.240 outputVoltage.u200 F 10

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru 169.254.1.240 outputVoltage.u200 F 12

echo 12V_supply at nominal bias

echo CarrierBoard is ON
