'''
Created on 8 May 2015

@author: up45
'''
from __future__ import unicode_literals, absolute_import

import unittest

import percival.carrier.const as const
from percival.carrier.devices import DeviceFamilyFeatures

        
class TestDeviceFamilyEnum(unittest.TestCase):
    def setUp(self):
        self.digipot = const.DeviceFamily.AD5242
        self.dac = const.DeviceFamily.AD5629
        self.adc = const.DeviceFamily.LTC2497
        
    def TestFunctions(self):
        self.assertIs(DeviceFamilyFeatures[self.digipot].function, const.DeviceFunction.control)
        self.assertIs(DeviceFamilyFeatures[self.dac].function, const.DeviceFunction.control)
        self.assertIs(DeviceFamilyFeatures[self.adc].function, const.DeviceFunction.monitoring)

    def TestDeviceID(self):
        self.assertIs(self.digipot.value, 0)
        self.assertIs(self.dac.value, 2)
        self.assertIs(self.adc.value, 4)
        
    def TestSupportedCommands(self):
        dev = DeviceFamilyFeatures[self.digipot]
        self.assertIs(dev.supports_cmd(const.DeviceCmd.no_operation),        True)
        self.assertIs(dev.supports_cmd(const.DeviceCmd.reset),               True)
        self.assertIs(dev.supports_cmd(const.DeviceCmd.initialize),          False)
        self.assertIs(dev.supports_cmd(const.DeviceCmd.set_and_get_value),   True)
        self.assertIs(dev.supports_cmd(const.DeviceCmd.set_word_value),      False)

        dev = DeviceFamilyFeatures[self.dac]
        self.assertIs(dev.supports_cmd(const.DeviceCmd.no_operation),        True)
        self.assertIs(dev.supports_cmd(const.DeviceCmd.reset),               True)
        self.assertIs(dev.supports_cmd(const.DeviceCmd.initialize),          True)
        self.assertIs(dev.supports_cmd(const.DeviceCmd.set_and_get_value),   True)
        self.assertIs(dev.supports_cmd(const.DeviceCmd.set_word_value),      False)
        
        dev = DeviceFamilyFeatures[self.adc]
        self.assertIs(dev.supports_cmd(const.DeviceCmd.no_operation),        True)
        self.assertIs(dev.supports_cmd(const.DeviceCmd.reset),               False)
        self.assertIs(dev.supports_cmd(const.DeviceCmd.initialize),          False)
        self.assertIs(dev.supports_cmd(const.DeviceCmd.set_and_get_value),   True)
        self.assertIs(dev.supports_cmd(const.DeviceCmd.set_word_value),      False)
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()