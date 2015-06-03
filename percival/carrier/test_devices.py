'''
Created on 8 May 2015

@author: up45
'''
from __future__ import unicode_literals, absolute_import

import unittest

import percival.carrier.devices as devices


class TestDevices(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testHeaderInfoInterface(self):
        """carrier.devices.HeaderInfo class implements the IDeviceSettings interface"""
        self.assertTrue(issubclass(devices.HeaderInfo, devices.IDeviceSettings), 
                        "HeaderInfo class does not fully implement the IDeviceSettings interface")
    
    def testControlChannelInterface(self):
        """carrier.devices.ControlChannel class implements the IDeviceSettings interface"""
        self.assertTrue(issubclass(devices.ControlChannel, devices.IDeviceSettings), 
                        "ControlChannel class does not fully implement the IDeviceSettings interface")

    def testMonitoringChannelsInterface(self):
        """carrier.devices.MonitoringChannel class implements the IDeviceSettings interface"""
        self.assertTrue(issubclass(devices.MonitoringChannel, devices.IDeviceSettings), 
                        "MonitoringChannel class does not fully implement the IDeviceSettings interface")

class TestHeaderInfo(unittest.TestCase):
    def setUp(self):
        self.dut = devices.HeaderInfo()
        
    def testMemMapAttributes(self):
        self.assertTrue(hasattr(self.dut, "eeprom_address"))
        self.assertTrue(hasattr(self.dut, "monitoring_channels_count"))
        self.assertTrue(hasattr(self.dut, "control_channels_count"))
        with self.assertRaises(AttributeError):
            self.dut.no_parameter_with_this_name
        self.assertTrue(hasattr(self.dut, "num_words"))
        
    def testParseValidMap(self):
        self.dut.parse_map([0xA1234567])
        self.assertEqual(0x23, self.dut.eeprom_address)
        self.assertEqual(0x45, self.dut.monitoring_channels_count)
        self.assertEqual(0x67, self.dut.control_channels_count)

    def testValidGenerateMap(self):
        self.dut.parse_map([0xA1234567])
        words = self.dut.generate_map()
        self.assertEqual([0x00234567], words)
        
    def testParseInvalidMap(self):
        """Empty map should raise index error and no values parsed"""
        with self.assertRaises(IndexError):
            self.dut.parse_map([])
        self.assertEqual(None, self.dut.eeprom_address)
        self.assertEqual(None, self.dut.monitoring_channels_count)
        self.assertEqual(None, self.dut.control_channels_count)

class TestControlChannel(unittest.TestCase):
    def setUp(self):
        self.dut = devices.ControlChannel()
        
    def testParseValidMap(self):
        # The full 5 word register is not yet in use in the firmware
        #self.dut.parse_map([0xA1234567, 0x89ABCDEF, 0x11223344, 0x55667788, 0x99AABBCC])
        self.dut.parse_map( [0xA1234567, 0x89ABCDEF, 0x11223344,             0x99AABBCC])
        self.assertEqual(0x01, self.dut.board_type)
        self.assertEqual(0x02, self.dut.component_family_id)
        self.assertEqual(0x00, self.dut.device_i2c_bus_select)
        self.assertEqual(0x1A, self.dut.channel_device_id)
        self.assertEqual(0x05, self.dut.channel_sub_address)
        self.assertEqual(0x67, self.dut.device_address)

        self.assertEqual(0x89AB, self.dut.channel_range_max)
        self.assertEqual(0xCDEF, self.dut.channel_range_min)

        self.assertEqual(0x1122, self.dut.channel_default_on)
        self.assertEqual(0x3344, self.dut.channel_default_off)

        # No yet in use in firmware
        #self.assertEqual(0x66, self.dut.channel_monitoring)
        #self.assertEqual(0x77, self.dut.safety_exception_threshold)
        #self.assertEqual(0x88, self.dut.read_frequency)

        self.assertEqual(0x00, self.dut.power_status)
        self.assertEqual(0xBBCC, self.dut.value)

    def testValidGenerateMap(self):
        # The full 5 word register is not yet in use in the firmware
        #self.dut.parse_map([0xA1234567, 0x89ABCDEF, 0x11223344, 0x55667788, 0x99AABBCC])
        self.dut.parse_map( [0xA1234567, 0x89ABCDEF, 0x11223344,             0x99AABBCC])
        words = self.dut.generate_map()
        #self.assertEqual([0x01234567, 0x89ABCDEF, 0x11223344, 0x00667788, 0x0000BBCC], words)
        self.assertEqual( [0x01234567, 0x89ABCDEF, 0x11223344,             0x0000BBCC], words)
        
    def testParseInvalidMap(self):
        """Empty map should raise index error and no values parsed"""
        with self.assertRaises(IndexError):
            self.dut.parse_map([0xA1234567, 0x89ABCDEF])
        self.assertEqual(None, self.dut.board_type)
        self.assertEqual(None, self.dut.component_family_id)
        self.assertEqual(None, self.dut.device_i2c_bus_select)
        self.assertEqual(None, self.dut.channel_device_id)
        self.assertEqual(None, self.dut.channel_sub_address)
        self.assertEqual(None, self.dut.device_address)

class TestCommand(unittest.TestCase):
    def setUp(self):
        self.dut = devices.Command()
        
    def testInitialMapFieldValue(self):
        self.assertIs(self.dut.device_index, None, "device_index should be initialised to None")
        self.assertTrue("device_index" in self.dut._mem_map.keys(), "No device index in: %s"%str(self.dut._mem_map.keys()))
        self.dut.device_index = 10
        self.assertIs(self.dut.device_index, 10, "device_index should now be set to 10, not %s"%str(self.dut.device_index))

class TestEchoWord(unittest.TestCase):
    def setUp(self):
        self.dut = devices.EchoWord()
        
    def testInitialMapFieldValue(self):
        self.assertIs(self.dut.read_value, None, "read_value should be initialised to None")
        self.assertTrue("read_value" in self.dut._mem_map.keys(), "No read_value in: %s"%str(self.dut._mem_map.keys()))
        self.dut.read_value = 10
        self.assertIs(self.dut.read_value, 10, "read_value should now be set to 10, not %s"%str(self.dut.read_value))

class TestReadValue(unittest.TestCase):
    def setUp(self):
        self.dut = devices.ReadValue()
        
    def testInitialMapFieldValue(self):
        self.assertIs(self.dut.sample_number, None, "sample_number should be initialised to None")
        self.assertTrue("sample_number" in self.dut._mem_map.keys(), "No sample_number in: %s"%str(self.dut._mem_map.keys()))
        self.dut.sample_number = 10
        self.assertIs(self.dut.sample_number, 10, "sample_number should now be set to 10, not %s"%str(self.dut.sample_number))
        
class TestMapField(unittest.TestCase):
    def setUp(self):
        self.dut = devices.MapField("TEST", 2, 3, 4)
        
    def TestProps(self):
        self.assertEqual(self.dut.num_bits, 3)
        self.assertEqual(self.dut.bit_offset, 4)
        self.assertEqual(self.dut.word_index, 2)
        self.assertEqual(self.dut.value, None)
        
    def TestValue(self):
        self.assertEqual(self.dut.value, None)
        self.dut.value = 45
        self.assertEqual(self.dut.value, 45)
        self.assertEqual(self.dut._value, 45)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()