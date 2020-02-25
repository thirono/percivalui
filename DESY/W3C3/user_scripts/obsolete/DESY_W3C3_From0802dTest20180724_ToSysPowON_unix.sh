percival-hl-system-command -c stop_acquisition
percival-hl-system-command -c exit_acquisition_armed_status

echo change biases from 08_2d_Test-status to standard-after-PowON-status 
percival-hl-scan-setpoints -i 08_2d_Test -f 08_1_CurrentBiases_ON_ready3T -n 4 -d 2000

echo Load default operating status
percival-hl-configure-clock-settings -i ./DESY/W3C3/config/01_Clock_Settings/ClockSettings_N05_120MHz.ini
percival-hl-configure-chip-readout-settings -i ./DESY/W3C3/config/02_Chip_Readout_Settings/ChipReadoutSettings_N05_3T_120MHz.ini
percival-hl-configure-system-settings -i ./DESY/W3C3/config/03_System_Settings/SystemSettings_N05_pixel_Test.ini

echo RESET DATA SYNCH STATUS...
# EXIT ARMED STATUS
percival-hl-system-command -c exit_acquisition_armed_status
# ASSERT CPNI FLAGS IN DEBUG REGISTERS
percival-hl-configure-sensor-debug -i ./DESY/W3C3/config/04_Sensor_Settings/SensorDebug_002_SET_CPNI.ini
# TOGGLE CPNI_EXT
percival-hl-set-system-setting -s ADVANCED_Enable_CPNI_EXT -v 1
percival-hl-set-system-setting -s ADVANCED_CPNI_EXT_options -v 1
percival-hl-set-system-setting -s ADVANCED_CPNI_EXT_options -v 2
percival-hl-set-system-setting -s ADVANCED_CPNI_EXT_options -v 1
percival-hl-set-system-setting -s ADVANCED_Enable_CPNI_EXT -v 0
# DEASSERT ALL FLAGS IN DEBUG REGISTERS
percival-hl-configure-sensor-debug -i ./DESY/W3C3/config/04_Sensor_Settings/SensorDebug_000_SAFE_START.ini
# ENTER ARMED STATUS
percival-hl-system-command -c enter_acquisition_armed_status
echo  DONE
