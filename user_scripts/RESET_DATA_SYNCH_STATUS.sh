echo -n RESET DATA SYNCH STATUS...
percival-hl-system-command -c exit_acquisition_armed_status
percival-hl-configure-sensor-debug -i ./config/04_Sensor_Settings/SensorDebug_002_SET_CPNI.ini
# ADVANCED_ENABLE_CPNI_EXT 1
# ADVANCED_CPNI_EXT_options 1
# ADVANCED_CPNI_EXT_options 2
# ADVANCED_CPNI_EXT_options 1
# ADVANCED_ENABLE_CPNI_EXT 0
percival-hl-configure-sensor-debug -i ./config/04_Sensor_Settings/SensorDebug_000_SAFE_START.ini
percival-hl-system-command -c enter_acquisition_armed_status
echo  DONE
