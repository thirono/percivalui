percival-hl-system-command -c stop_acquisition
percival-hl-system-command -c exit_acquisition_armed_status

echo "change biases from standard-after-PowON-status to 08_17a-status , BSI02 3T"  
percival-hl-scan-setpoints -i 08_1_CurrentBiases_ON_ready3T -f 08_17a_BSI02_3T_FSkip -n 4 -d 2000

echo "Load ADC40MHz, PLL120MHz, 3T, SequentialMode (FSkip), 10 Images, 12ms integration"
percival-hl-configure-clock-settings -i ./DESY/W3C3/config/01_Clock_Settings/ClockSettings_N17_ADC40MHz_PLL120MHz.ini
percival-hl-configure-chip-readout-settings -i ./DESY/W3C3/config/02_Chip_Readout_Settings/ChipReadoutSettings_N17_3T_PGAB_ADC40MHz_PLL120MHz_SeqFSkip.ini
# percival-hl-configure-chip-readout-settings -i ./DESY/W3C3/config/02_Chip_Readout_Settings/ChipReadoutSettings_N17_LuigiExample_FSkip.ini
percival-hl-configure-system-settings -i ./DESY/W3C3/config/03_System_Settings/SystemSettings_N17_pixel_10Img_12ms_SEQUENTIAL.ini

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
echo   BSI02 BSI02 BSI02 BSI02 BSI02 BSI02 BSI02 BSI02 BSI02 BSI02 BSI02 BSI02 
echo   3T 3T 3T 3T 3T 3T 3T 3T 3T 3T 3T 3T 3T 3T 3T 3T 3T 3T 3T 3T 3T 3T 3T 3T 3T
