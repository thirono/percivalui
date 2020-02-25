echo -n RESET DATA SYNCH STATUS...
# EXIT ARMED STATUS
percival-hl-system-command -c exit_acquisition_armed_status

# ASSERT dmuxSEL, CPNI FLAGS IN DEBUG REGISTERS
percival-hl-configure-sensor-debug -i ./DESY/W3C3/config/04_Sensor_Settings/SensorDebug_0xx_SET_CPNI_nd_dmxSEL.ini

# Set external dmuxSEL to Force Low and enable it
percival-hl-set-system-setting -s ADVANCED_dmuxSEL_EXT_options -v 2
percival-hl-set-system-setting -s ADVANCED_Enable_dmuxSEL_EXT -v 1
percival-hl-set-system-setting -s ADVANCED_dmuxSEL_EXT_options -v 2
percival-hl-set-system-setting -s ADVANCED_dmuxSEL_EXT_options -v 1

# TOGGLE CPNI_EXT
percival-hl-set-system-setting -s ADVANCED_Enable_CPNI_EXT -v 1
percival-hl-set-system-setting -s ADVANCED_CPNI_EXT_options -v 1
percival-hl-set-system-setting -s ADVANCED_CPNI_EXT_options -v 2
percival-hl-set-system-setting -s ADVANCED_CPNI_EXT_options -v 1
percival-hl-set-system-setting -s ADVANCED_Enable_CPNI_EXT -v 0

# DEASSERT CPNI_EXT IN DEBUG REGISTER (but keep dmuxSEL flag)
percival-hl-configure-sensor-debug -i ./DESY/W3C3/config/04_Sensor_Settings/SensorDebug_0xx_SET_dmxSEL.ini

# ENTER ARMED STATUS
percival-hl-system-command -c enter_acquisition_armed_status
echo  DONE
echo NO dmxSEL NO dmxSEL NO dmxSEL NO dmxSEL NO dmxSEL NO dmxSEL NO dmxSEL NO dmxSEL
