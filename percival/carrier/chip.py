from __future__ import print_function

import logging
from percival.carrier import const
from percival.carrier.registers import UARTRegister


class ChipReadoutSettings(object):
    def __init__(self, txrx, settings_ini=None):
        """
        Constructor

        :param txrx: Percival communication context
        :type  txrx: TxRx
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self._txrx = txrx
        self._reg_command = UARTRegister(const.CHIP_READOUT_SETTINGS)
        self._reg_command.initialize_map([0, 0, 0, 0, 0, 0, 0, 0,
                                          0, 0, 0, 0, 0, 0, 0, 0,
                                          0, 0, 0, 0, 0, 0, 0, 0,
                                          0, 0, 0, 0, 0, 0, 0, 0])
        self._settings_ini = None
        if settings_ini:
            self.load_ini(settings_ini)

    def load_ini(self, settings_ini):
        """
        Load settings from ini file into the registers ready for writing to hardware
        :param settings_ini:
        :return:
        """
        self._settings_ini = settings_ini
        map = self._settings_ini.value_map
        self.log.info(map)
        # First replace any true or false with 1 or 0
        for item in map:
            if isinstance(map[item], str):
                if 'false' in map[item].lower():
                    map[item] = 0
                elif 'true' in map[item].lower():
                    map[item] = 1
        # Now set the attributes within the UART Register
        for item in map:
            try:
                if hasattr(self._reg_command.fields, item):
                    setattr(self._reg_command.fields, item, int(map[item]))
                else:
                    self.log.debug("No register found for ini file setting %s", item)
            except:
                self.log.error("Failed to set iten %s from ini file", item)
                raise

    def _send_to_carrier(self):
        """
        Private method to construct and send a system command.

        This method gets the TxMessage object representation of the system command
        and sends it through the txrx object to the Percival hardware, returning any
        response.

        Returns nothing as the lower level checks for expected response.
        Can raise RuntimeError if the expected response is not received.

        :param cmd: command to encode
        :type  cmd: SystemCmd
        """
        cmd_msgs = self._reg_command.get_write_cmd_msg(eom=True)
        for cmd_msg in cmd_msgs:
            self._txrx.send_recv_message(cmd_msg)

    def download_settings(self):
        self._send_to_carrier()

