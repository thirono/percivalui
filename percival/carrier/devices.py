'''
Created on 8 May 2015

@author: Ulrik Pedersen
'''
from __future__ import unicode_literals, absolute_import
from percival.carrier.const import DeviceFamily, DeviceCmd, DeviceFunction

import logging
logger = logging.getLogger(__name__)


class DeviceFeatures(object):
    """Mapping PCB devices to their supported functionality
    
    This represent the documented table "Supported DEVICE_CMD vs device family"
    """
    def __init__(self, device_family_id, function, description="", commands=[]):
        """
            :param device_family_id: The integer device ID as documented
            :type  device_family_id: `int`
            :param function:  The enumerated functionality of the device
            :type  function:  `DeviceFunction` item
            :param description: Human readable description of the device
            :type  description: string
            :param commands: Supported commands for this device
            :type  commands: list of `DeviceCmd` items
        """
        self._device_family_id = device_family_id
        self._function = function
        self._description = description
        self._commands = commands
        
    @property
    def device_family_id(self):
        return self._device_family_id

    @property
    def function(self):
        return self._function

    @property
    def description(self):
        return self._description
    
    def supports_cmd(self, cmd):
        """Check if a given command is supported for this device
        
            :param cmd: The command to check for
            :type cmd:  `DeviceCmd`
            :returns: True if the command is supported, False if not.
            :rtype: boolean
        """
        return cmd in self._commands
        

DeviceFamilyFeatures = {
    DeviceFamily.AD5242:   DeviceFeatures(DeviceFamily.AD5242, DeviceFunction.control,
                                          "Digital potentiometer",
                                          [DeviceCmd.no_operation,
                                           DeviceCmd.reset,
                                           DeviceCmd.set_value,
                                           DeviceCmd.get_value,
                                           DeviceCmd.set_and_get_value,
                                           DeviceCmd.set_value_on,
                                           DeviceCmd.set_value_off] ),
    DeviceFamily.AD5263:   DeviceFeatures(DeviceFamily.AD5263, DeviceFunction.control,
                                          "Digital potentiometer",
                                          [DeviceCmd.no_operation,
                                           DeviceCmd.reset,
                                           DeviceCmd.set_value,
                                           DeviceCmd.get_value,
                                           DeviceCmd.set_and_get_value] ),
    DeviceFamily.AD5629:   DeviceFeatures(DeviceFamily.AD5629, DeviceFunction.control,
                                          "DAC for control",
                                          [DeviceCmd.no_operation,
                                           DeviceCmd.reset,
                                           DeviceCmd.initialize,
                                           DeviceCmd.set_value,
                                           DeviceCmd.get_value,
                                           DeviceCmd.set_and_get_value,
                                           DeviceCmd.enable_standby_mode,
                                           DeviceCmd.disable_standby_mode] ),
    DeviceFamily.AD5669:   DeviceFeatures(DeviceFamily.AD5669, DeviceFunction.control,
                                          "DAC for control",
                                          [DeviceCmd.no_operation,
                                           DeviceCmd.reset,
                                           DeviceCmd.initialize,
                                           DeviceCmd.set_value,
                                           DeviceCmd.get_value,
                                           DeviceCmd.set_and_get_value,
                                           DeviceCmd.enable_standby_mode,
                                           DeviceCmd.disable_standby_mode] ),
    DeviceFamily.LTC2309:  DeviceFeatures(DeviceFamily.LTC2309, DeviceFunction.monitoring,
                                          "ADC for monitoring",
                                          [DeviceCmd.no_operation,
                                           DeviceCmd.set_value,
                                           DeviceCmd.get_value,
                                           DeviceCmd.set_and_get_value]),
    DeviceFamily.LTC2497:  DeviceFeatures(DeviceFamily.LTC2497, DeviceFunction.monitoring,
                                          "ADC for monitoring",
                                          [DeviceCmd.no_operation,
                                           DeviceCmd.set_value,
                                           DeviceCmd.get_value,
                                           DeviceCmd.set_and_get_value]),
    DeviceFamily.MAX31730: DeviceFeatures(DeviceFamily.MAX31730, DeviceFunction.monitoring,
                                          "Temperature for monitoring",
                                          [DeviceCmd.no_operation,
                                           DeviceCmd.reset,
                                           DeviceCmd.initialize,
                                           DeviceCmd.set_and_get_value]),
    DeviceFamily.AT24CM01: DeviceFeatures(DeviceFamily.AT24CM01, DeviceFunction.eeprom,
                                          "EEPROM for on-board storage",
                                          [DeviceCmd.no_operation,
                                           DeviceCmd.set_word_value,
                                           DeviceCmd.get_word_value,
                                           DeviceCmd.set_page_value,
                                           DeviceCmd.get_page_value]),
    }

