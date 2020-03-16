#!/bin/bash

# Switch the WIENER ON

# ./mainswitchON.sh

# Switch the CarrierBoard On

# echo Switching the CarrierBoard ON

# sleep 5

# Set all values to 0 V and current limits

WIENER_IP=172.23.16.179

echo Setting current limit, and voltage to 0

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u200 F 0
snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputCurrent.u200 F 6

if [ $? -ne 0 ]
then
 echo Failed to set current value on u200
 exit 2
else
 echo All channels set properly 
fi



sleep 2

#Switch everything ON

echo Switching channel ON

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputSwitch.u200 i 1

echo All channels switched ON

sleep 2

#Set the values

#12V_supply

echo Ramping 12V_supply up

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u200 F 2

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u200 F 4

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u200 F 6

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u200 F 8

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u200 F 10

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u200 F 12

echo 12V_supply at nominal bias

echo CarrierBoard is ON
