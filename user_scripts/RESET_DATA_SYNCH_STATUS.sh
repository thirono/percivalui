echo -n RESET DATA SYNCH STATUS...
percival-hl-system-command -c exit_acquisition_armed_status

percival-hl-system-command -c enter_acquisition_armed_status
echo  DONE