'''
Created on 8 May 2015

@author: up45
'''
from __future__ import unicode_literals, absolute_import

import unittest
from mock import MagicMock, call

import percival.carrier.const as const
from percival.carrier.devices import DeviceFamily, DeviceFamilyFeatures, AD5263, MAX31730, LTC2309

        
class TestDeviceFamilyEnum(unittest.TestCase):
    def setUp(self):
        self.digipot = const.DeviceFamily.AD5242
        self.dac = const.DeviceFamily.AD5629
        self.adc = const.DeviceFamily.LTC2497
        
    def TestFunctions(self):
        self.assertIs(DeviceFamilyFeatures[self.digipot].function, const.DeviceFunction.control)
        self.assertIs(DeviceFamilyFeatures[self.digipot].device_family_id, const.DeviceFamily.AD5242)
        self.assertEquals(DeviceFamilyFeatures[self.digipot].description, "Digital potentiometer")
        self.assertIs(DeviceFamilyFeatures[self.dac].function, const.DeviceFunction.control)
        self.assertIs(DeviceFamilyFeatures[self.dac].device_family_id, const.DeviceFamily.AD5629)
        self.assertEquals(DeviceFamilyFeatures[self.dac].description, "DAC for control")
        self.assertIs(DeviceFamilyFeatures[self.adc].function, const.DeviceFunction.monitoring)
        self.assertIs(DeviceFamilyFeatures[self.adc].device_family_id, const.DeviceFamily.LTC2497)
        self.assertEquals(DeviceFamilyFeatures[self.adc].description, "ADC for monitoring")

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

    def TestDeviceAD5263(self):
        channel = MagicMock()
        ad5263 = AD5263("test1", channel)
        # Check the name is correct
        self.assertEqual(ad5263.name, "test1")
        # Check the device is correct
        self.assertEqual(ad5263.device, DeviceFamily.AD5263.name)
        # Issue a set
        ad5263.set_value(10, 0.2)
        # Verify the mock was called with the correct statement
        channel.set_value.assert_called_with(10, 0.2)

    def TestDeviceMAX31730(self):
        channel = MagicMock()
        channel._channel_ini.Offset = 10.0
        channel._channel_ini.Divider = 2.0
        channel._channel_ini.Unit = "C"
        reply_data = MagicMock()
        reply_data.i2c_communication_error = 0
        reply_data.read_value = 50
        channel.get_value = MagicMock(return_value=reply_data)

        max31730 = MAX31730("test1", channel)
        self.assertEqual(max31730.name, "test1")
        self.assertEqual(max31730.device, "MAX31730")
        data = MagicMock()
        data.below_low_threshold = 0
        data.below_extreme_low_threshold = 0
        data.above_high_threshold = 1
        data.above_extreme_high_threshold = 0
        data.safety_exception_detected = 0
        data.i2c_communication_error = 0
        data.read_value = 100
        max31730.update(data)

        self.assertAlmostEqual(max31730.temperature, 45.0)
        self.assertEqual(max31730.unit, "C")
        json = max31730.status
        self.assertEqual(json["unit"], "C")
        self.assertEqual(json["device"], "MAX31730")
        self.assertEqual(json["low_threshold"], 0)
        self.assertEqual(json["extreme_low_threshold"], 0)
        self.assertEqual(json["high_threshold"], 1)
        self.assertEqual(json["extreme_high_threshold"], 0)
        self.assertEqual(json["i2c_comms_error"], 0)
        self.assertAlmostEqual(json["temperature"], 45.0)
        # Update without any provided data
        max31730.update()
        self.assertAlmostEqual(max31730.temperature, 20.0)

    def TestDeviceLTC2309(self):
        channel = MagicMock()
        channel._channel_ini.Offset = 20.0
        channel._channel_ini.Divider = 4.0
        channel._channel_ini.Unit = "V"
        reply_data = MagicMock()
        reply_data.i2c_communication_error = 0
        reply_data.read_value = 80
        channel.get_value = MagicMock(return_value=reply_data)

        ltc2309 = LTC2309("test2", channel)
        self.assertEqual(ltc2309.name, "test2")
        self.assertEqual(ltc2309.device, "LTC2309")
        data = MagicMock()
        data.below_low_threshold = 1
        data.below_extreme_low_threshold = 0
        data.above_high_threshold = 0
        data.above_extreme_high_threshold = 0
        data.safety_exception_detected = 0
        data.i2c_communication_error = 1
        data.read_value = 200
        ltc2309.update(data)

        self.assertAlmostEqual(ltc2309.voltage, 45.0)
        self.assertEqual(ltc2309.unit, "V")
        json = ltc2309.status
        self.assertEqual(json["unit"], "V")
        self.assertEqual(json["device"], "LTC2309")
        self.assertEqual(json["low_threshold"], 1)
        self.assertEqual(json["extreme_low_threshold"], 0)
        self.assertEqual(json["high_threshold"], 0)
        self.assertEqual(json["extreme_high_threshold"], 0)
        self.assertEqual(json["i2c_comms_error"], 1)
        self.assertAlmostEqual(json["voltage"], 45.0)
        # Update without any provided data
        ltc2309.update()
        self.assertAlmostEqual(ltc2309.voltage, 15.0)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()