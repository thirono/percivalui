#!/bin/bash

# Switch the WIENER ON

# ./mainswitchON.sh

# Switch the PowerBoard On

# echo Switching the PowerBoard ON

# sleep 5

# Set all values to 0 V and current limits

WIENER_IP=172.23.16.179

echo Setting all current limits and all voltages to 0

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u0 F 0		 
snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputCurrent.u0 F 3
		
snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u1 F 0
snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputCurrent.u1 F 0.5

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u2 F 0
snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputCurrent.u2 F 1.5

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u3 F 0
snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputCurrent.u3 F 1

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u4 F 0
snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputCurrent.u4 F 0.5

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u5 F 0
snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputCurrent.u5 F 0.5

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u6 F 0
snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputCurrent.u6 F 0.1

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u7 F 0
snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputCurrent.u7 F 0.5

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u100 F 0		 
snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputCurrent.u100 F 0.3
		
snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u101 F 0
snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputCurrent.u101 F 0.4

echo All channels set propertly 

#Switch everything ON

echo Switching every channel ON

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputSwitch.u0 i 1

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputSwitch.u1 i 1

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputSwitch.u2 i 1

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputSwitch.u3 i 1

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputSwitch.u4 i 1

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputSwitch.u5 i 1

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputSwitch.u6 i 1

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputSwitch.u7 i 1

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputSwitch.u100 i 1

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputSwitch.u101 i 1

sleep 5

echo All channels switched ON

#Set the values

#5V1_supply

echo Ramping 5V1_supply up

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u5 F 1

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u5 F 2

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u5 F 3

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u5 F 4

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u5 F 5

echo 5V1_supply at nominal bias

#3V3_supply

echo Ramping 3V3_supply up

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u6 F 0.66

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u6 F 1.32

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u6 F 1.98

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u6 F 2.64

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u6 F 3.3

echo 3V3_supply at nominal bias

#Vcontr_all

echo Ramping Vcontr_all up

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u4 F 1.2

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u4 F 2.4

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u4 F 3.6

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u4 F 4.8

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u4 F 6

echo Vcontr_all at nominal bias

#Vreg_3V3 

echo Ramping Vreg_3V3 up

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u0 F 0.78

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u0 F 1.56

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u0 F 2.34

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u0 F 3.12

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u0 F 3.9

echo Vreg_3V3 at nominal bias

#Vreg_1V8

echo Ramping Vreg_1V8 up

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u2 F 0.46

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u2 F 0.92

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u2 F 1.38

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u2 F 1.84

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u2 F 2.3

echo Vreg_1V8 at nominal bias

#Vreg_2V3 

echo Ramping Vreg_2V3 up

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u3 F 0.7

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u3 F 1.4

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u3 F 2.1

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u3 F 2.8

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u3 F 3.5

echo Vreg_2V3 at nominal bias

#Vreg_0V7

echo Ramping Vreg_0V7 up

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u1 F 0.3

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u1 F 0.6

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u1 F 0.9

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u1 F 1.2

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u1 F 1.5

echo Vreg_0V7 at nominal bias

#PIXELRING

echo Ramping PIXELRING up

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u7 F 1

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u7 F 2

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u7 F 3

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u7 F 4

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u7 F 5

echo PIXELRING at nominal bias

#8V_supply & m8V_supply

echo Ramping 8V_supply up STEP 1

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u100 F 1

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u100 F 2

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u100 F 3

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u100 F 4

echo Ramping m8V_supply up STEP 1

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u101 F 1

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u101 F 2

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u101 F 3

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u101 F 4

echo Ramping 8V_supply up STEP 2

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u100 F 5

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u100 F 6

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u100 F 7

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u100 F 8

echo Ramping m8V_supply up STEP 2

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u101 F 5

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u101 F 6

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u101 F 7

snmpset -v 2c -m +WIENER-CRATE-MIB -c guru $WIENER_IP outputVoltage.u101 F 8

echo 8V_supply and m8V_supply at nominal bias

sleep 2

echo PowerBoard is ON
