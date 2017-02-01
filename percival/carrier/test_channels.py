'''
Created on 8 May 2015

@author: up45
'''
from __future__ import unicode_literals, absolute_import

import unittest, sys, logging
from mock import MagicMock, call
from builtins import bytes

import percival.carrier.const as const
from percival.carrier.channels import ControlChannel, MonitoringChannel
from percival.carrier.txrx import TxMessage
from percival.carrier.errors import PercivalControlDeviceError


class TestChannels(unittest.TestCase):

    def setUp(self):
        # Perform any setup here
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(logging.DEBUG)
        self.txrx = MagicMock()
        self.channel_ini = MagicMock()
        self.settings = [(0x00, 0x00), (0x00, 0x00), (0x00, 0x00), (0x00, 0x00)]

    def TestControlChannel(self):
        self.txrx.send_recv_message = MagicMock(return_value=[(0x03EE, 0x00000019)])
        self.channel_ini.Component_family_ID = const.DeviceFamily.AD5669
        self.channel_ini._channel_number = 1
        self.channel_ini.UART_address = 10
        self.channel_ini.Board_type = const.BoardTypes.bottom
        ctrlChannel = ControlChannel(self.txrx, self.channel_ini, self.settings)
        # Verify the txrx mock had send_rcv_message called
        self.txrx.send_recv_message.assert_called_with(
            TxMessage(bytes("\x03\x3A\x20\x00\x00\x01", encoding="latin-1"), expect_eom=True))

        # Send a no-op command
        self.txrx.send_recv_message.reset_mock()
        ctrlChannel.cmd_no_operation()
        # Verify the txrx mock had send_rcv_message called
        self.txrx.send_recv_message.assert_called_with(
            TxMessage(bytes("\x03\x3A\x00\x00\x00\x01", encoding="latin-1"), expect_eom=True))

        # Send a set and get value
        self.txrx.send_recv_message.reset_mock()
        ctrlChannel.cmd_set_and_get_value()
        # Verify the txrx mock had send_rcv_message called
        self.txrx.send_recv_message.assert_called_with(
            TxMessage(bytes("\x03\x3A\x50\x00\x00\x01", encoding="latin-1"), expect_eom=True))


        # Send a read echo word command
        self.txrx.send_recv_message.reset_mock()
        ctrlChannel.read_echo_word()
        # Verify the txrx mock had send_rcv_message called
        self.txrx.send_recv_message.assert_called_with(
            TxMessage(bytes("\x04\x06\x00\x00\x00\x00", encoding="latin-1"), expect_eom=False))

        # Set the value to 10
        self.txrx.send_recv_message.reset_mock()
        ctrlChannel.cmd_control_set_value(10)
        # Verify the txrx mock had send_rcv_message called
        self.txrx.send_recv_message.assert_called_with(
            TxMessage(bytes("\x00\x0D\x00\x00\x00\x0A", encoding="latin-1"), expect_eom=True))

        # Set the value to 20
        self.txrx.send_recv_message.reset_mock()
        ctrlChannel.cmd_control_set_value(20)
        # Verify the txrx mock had send_rcv_message called
        self.txrx.send_recv_message.assert_called_with(
            TxMessage(bytes("\x00\x0D\x00\x00\x00\x14", encoding="latin-1"), expect_eom=True))

        # Set the value to 25 from the control point
        self.txrx.send_recv_message.reset_mock()
        ctrlChannel.set_value(25)
        # Verify the txrx mock had send_rcv_message called
        calls = self.txrx.send_recv_message.mock_calls
        self.assertEqual(calls[0], call(
            # Command: no-op on device index 1
            TxMessage(bytes("\x03\x3A\x00\x00\x00\x01", encoding="latin-1"), expect_eom=True)))
        self.assertEqual(calls[1], call(
            # Set Control value on UART addr 0x000D to 25 (=0x19)
            TxMessage(bytes("\x00\x0D\x00\x00\x00\x19", encoding="latin-1"), expect_eom=True)))
        self.assertEqual(calls[2], call(
            # Command: no-op on device index 1
            TxMessage(bytes("\x03\x3A\x00\x00\x00\x01", encoding="latin-1"), expect_eom=True)))
        self.assertEqual(calls[3], call(
            # Command: set_and_get_value on device index 1
            TxMessage(bytes("\x03\x3A\x50\x00\x00\x01", encoding="latin-1"), expect_eom=True)))
        self.assertEqual(calls[4], call(
            # Readback READ ECHO WORD
            TxMessage(bytes("\x04\x06\x00\x00\x00\x00", encoding="latin-1"), expect_eom=False)))

        # Set the value to 26 from the control point
        self.txrx.send_recv_message.reset_mock()
        # Verify this times out and raises a runtime error
        with self.assertRaises(PercivalControlDeviceError):
            ctrlChannel.set_value(26, 0.01)

        # Set the value to 25 from the control point
        self.txrx.send_recv_message.reset_mock()
        # Set the mock to return an i2c error
        self.txrx.send_recv_message.return_value = [(0x03EE, 0x00010019)]
        # Verify this raises an IO error
        with self.assertRaises(IOError):
            ctrlChannel.set_value(25)

        # Set the value to 0x42 from the control point
        self.txrx.send_recv_message.reset_mock()
        # Set the mock to return a larger value
        self.txrx.send_recv_message.return_value = [(0x03EE, 0x00000044)]
        # Verify this raises an exception
        with self.assertRaises(PercivalControlDeviceError):
            ctrlChannel.set_value(0x42)

    def TestAD5242ControlChannel(self):
        self.channel_ini.reset_mock()
        self.txrx.send_recv_message = MagicMock(return_value=[(0x03EE, 0x00000019)])
        self.channel_ini.Component_family_ID = const.DeviceFamily.AD5242
        self.channel_ini._channel_number = 52
        self.channel_ini.UART_address = 214
        self.channel_ini.Board_type = const.BoardTypes.bottom
        ctrlChannel = ControlChannel(self.txrx, self.channel_ini, self.settings)
        ctrlChannel.cmd_control_set_value(10)
        # Verify the txrx mock had send_rcv_message called
        self.txrx.send_recv_message.assert_called_with(
            TxMessage(bytes("\x00\xD9\x00\x01\x00\x0A", encoding="latin-1"), expect_eom=True))

    def TestMonitoringChannel(self):
        self.txrx.send_recv_message = MagicMock(return_value=[(0x03EE, 0x01000023)])
        self.channel_ini.Component_family_ID = const.DeviceFamily.MAX31730
        self.channel_ini._channel_number = 18
        self.channel_ini.UART_address = 139
        self.channel_ini.Board_type = const.BoardTypes.carrier
        mntrChannel = MonitoringChannel(self.txrx, self.channel_ini, self.settings)

        # Call get value on the monitor
        self.txrx.send_recv_message.reset_mock()
        with self.assertRaises(RuntimeError):
            mntrChannel.get_value()
        # Verify the txrx mock had send_rcv_message called
        calls = self.txrx.send_recv_message.mock_calls
        self.assertEqual(calls[0], call(
            TxMessage(bytes("\x04\x06\x00\x00\x00\x00", encoding="latin-1"), expect_eom=False)))
        self.assertEqual(calls[1], call(
            TxMessage(bytes("\x03\x3A\x00\x80\x00\x12", encoding="latin-1"), expect_eom=True)))
        self.assertEqual(calls[2], call(
            TxMessage(bytes("\x03\x3A\x50\x80\x00\x12", encoding="latin-1"), expect_eom=True)))
        self.assertEqual(calls[3], call(
            TxMessage(bytes("\x04\x06\x00\x00\x00\x00", encoding="latin-1"), expect_eom=False)))

        # Setup the mock with different sample numbers
        self.txrx.send_recv_message = MagicMock() #return_value=[(0x03EE, 0x01000023), (0x03EE, 0x02000023)])
        self.txrx.send_recv_message.side_effect = [[(0x03EE, 0x01000012)],
                                                   [(0x03EE, 0xABBABAC1)],
                                                   [(0x03EE, 0xABBABAC1)],
                                                   [(0x03EE, 0x02000013)]]
        mntrChannel = MonitoringChannel(self.txrx, self.channel_ini, self.settings)
        self.txrx.send_recv_message.reset_mock()
        value = mntrChannel.get_value()
        self.assertEquals(value.read_value, 19)

        # Setup the mock to return i2c error
        self.txrx.send_recv_message = MagicMock() #return_value=[(0x03EE, 0x01000023), (0x03EE, 0x02000023)])
        self.txrx.send_recv_message.side_effect = [[(0x03EE, 0x01010012)],
                                                   [(0x03EE, 0xABBABAC1)],
                                                   [(0x03EE, 0xABBABAC1)],
                                                   [(0x03EE, 0x02010013)]]
        # Verify this raises an IO error
        with self.assertRaises(IOError):
            value = mntrChannel.get_value()

