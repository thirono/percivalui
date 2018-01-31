echo PERCIVAL EMULATED POWERDOWN STARTED

echo - Exit armed status
percival-hl-system-command -c stop_acquisition
percival-hl-system-command -c forced_stop_acquisition
percival-hl-system-command -c exit_acquisition_armed_status

echo - Loading initial safe status...
percival-hl-configure-clock-settings -i ./config/01_Clock_Settings/ClockSettings_000_SAFE_START.ini
percival-hl-configure-chip-readout-settings -i ./config/02_Chip_Readout_Settings/ChipReadoutSettings_000_SAFEstart.ini
percival-hl-configure-system-settings -i ./config/03_System_Settings/SystemSettings_000_SAFE_START.ini

# percival-hl-scan-setpoints -i 08_0_CurrentBiases_ON -f 07_0_VoltageReferences_ON -n 4 -d 2000
# percival-hl-scan-setpoints -i 07_0_VoltageReferences_ON -f 06_0_PixelVoltages_ON -n 4 -d 2000
# percival-hl-scan-setpoints -i 06_0_PixelVoltages_ON -f 05_0_PixelVoltages_ON -n 4 -d 2000
# percival-hl-scan-setpoints -i 05_0_PixelVoltages_ON -f 04_0_PixelVoltages_ON -n 4 -d 2000
# percival-hl-scan-setpoints -i 04_0_PixelVoltages_ON -f 03_0_PixelVoltages_ON -n 4 -d 2000
# percival-hl-scan-setpoints -i 03_0_PixelVoltages_ON -f 02_0_LVDS_ON -n 4 -d 2000
percival-hl-system-command -c disable_LVDS_IOs
# percival-hl-scan-setpoints -i 02_0_LVDS_ON -f 01_0_VDD_ON -n 4 -d 2000
# percival-hl-scan-setpoints -i 01_0_VDD_ON -f 00_0_0V0A -n 4 -d 2000

echo PERCIVAL EMULATED POWERDOWN COMPLETED
