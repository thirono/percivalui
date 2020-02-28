echo PERCIAL setup to monitor Temperatures
echo

echo - Downloading device settings, enabling global monitoring
percival-hl-download-channel-settings
percival-hl-system-command -c enable_global_monitoring

echo - defining monitoring grps
percival-hl-configure-monitor-groups -i ./DESY/W3C3/config/05_Spreadsheets/DESY_W3C3_Group_Definitions.xls

echo DONE, use OdinCntrl status panel
