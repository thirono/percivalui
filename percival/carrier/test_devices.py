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


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()