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


class TestChannels(unittest.TestCase):

    def setUp(self):
        # Perform any setup here
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(logging.DEBUG)
        self.txrx = MagicMock()
        self.channel_ini = MagicMock()
        self.settings = [(0x00, 0x00), (0x00, 0x00), (0x00, 0x00), (0x00, 0x00)]

    def TestControlChannel(self):
        self.txrx.send_recv_message = MagicMock(return_value=[(0x01B2, 0x00000019)])
        self.channel_ini.Component_family_ID = const.DeviceFamily.AD5629
        self.channel_ini._channel_number = 5
        self.channel_ini.UART_address = 19
        self.channel_ini.Board_type = const.BoardTypes.carrier
        ctrlChannel = ControlChannel(self.txrx, self.channel_ini, self.settings)
        # Verify the txrx mock had send_rcv_message called
        self.txrx.send_recv_message.assert_called_with(
            TxMessage(bytes("\x01\x70\x20\x00\x00\x05", encoding="latin-1"), expect_eom=True))

        # Send a no-op command
        self.txrx.send_recv_message.reset_mock()
        ctrlChannel.cmd_no_operation()
        # Verify the txrx mock had send_rcv_message called
        self.txrx.send_recv_message.assert_called_with(
            TxMessage(bytes("\x01\x70\x00\x00\x00\x05", encoding="latin-1"), expect_eom=True))

        # Send a set and get value
        self.txrx.send_recv_message.reset_mock()
        ctrlChannel.cmd_set_and_get_value()
        # Verify the txrx mock had send_rcv_message called
        self.txrx.send_recv_message.assert_called_with(
            TxMessage(bytes("\x01\x70\x50\x00\x00\x05", encoding="latin-1"), expect_eom=True))


        # Send a read echo word command
        self.txrx.send_recv_message.reset_mock()
        ctrlChannel.read_echo_word()
        # Verify the txrx mock had send_rcv_message called
        self.txrx.send_recv_message.assert_called_with(
            TxMessage(bytes("\x01\xCA\x00\x00\x00\x00", encoding="latin-1"), expect_eom=False))

        # Set the value to 10
        self.txrx.send_recv_message.reset_mock()
        ctrlChannel.cmd_control_set_value(10)
        # Verify the txrx mock had send_rcv_message called
        self.txrx.send_recv_message.assert_called_with(
            TxMessage(bytes("\x00\x16\x00\x00\x00\x0A", encoding="latin-1"), expect_eom=True))

        # Set the value to 20
        self.txrx.send_recv_message.reset_mock()
        ctrlChannel.cmd_control_set_value(20)
        # Verify the txrx mock had send_rcv_message called
        self.txrx.send_recv_message.assert_called_with(
            TxMessage(bytes("\x00\x16\x00\x00\x00\x14", encoding="latin-1"), expect_eom=True))


        # Set the value to 25 from the control point
        self.txrx.send_recv_message.reset_mock()
        ctrlChannel.set_value(25)
        # Verify the txrx mock had send_rcv_message called
        calls = self.txrx.send_recv_message.mock_calls
        self.assertEqual(calls[0], call(
            TxMessage(bytes("\x01\x70\x00\x00\x00\x05", encoding="latin-1"), expect_eom=True)))
        self.assertEqual(calls[1], call(
            TxMessage(bytes("\x00\x16\x00\x00\x00\x19", encoding="latin-1"), expect_eom=True)))
        self.assertEqual(calls[2], call(
            TxMessage(bytes("\x01\x70\x00\x00\x00\x05", encoding="latin-1"), expect_eom=True)))
        self.assertEqual(calls[3], call(
            TxMessage(bytes("\x01\x70\x50\x00\x00\x05", encoding="latin-1"), expect_eom=True)))
        self.assertEqual(calls[4], call(
            TxMessage(bytes("\x01\xCA\x00\x00\x00\x00", encoding="latin-1"), expect_eom=False)))

    def TestAD5242ControlChannel(self):
        self.txrx.send_recv_message = MagicMock(return_value=[(0x01B2, 0x00000019)])
        self.channel_ini.Component_family_ID = const.DeviceFamily.AD5242
        self.channel_ini._channel_number = 5
        self.channel_ini.UART_address = 19
        self.channel_ini.Board_type = const.BoardTypes.carrier
        ctrlChannel = ControlChannel(self.txrx, self.channel_ini, self.settings)
        ctrlChannel.cmd_control_set_value(10)
        # Verify the txrx mock had send_rcv_message called
        self.txrx.send_recv_message.assert_called_with(
            TxMessage(bytes("\x00\x16\x00\x01\x00\x0A", encoding="latin-1"), expect_eom=True))

    def TestMonitoringChannel(self):
        self.txrx.send_recv_message = MagicMock(return_value=[(0x01B2, 0x01000023)])
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
            TxMessage(bytes("\x01\xCA\x00\x00\x00\x00", encoding="latin-1"), expect_eom=False)))
        self.assertEqual(calls[1], call(
            TxMessage(bytes("\x01\x70\x00\x80\x00\x12", encoding="latin-1"), expect_eom=True)))
        self.assertEqual(calls[2], call(
            TxMessage(bytes("\x01\x70\x50\x80\x00\x12", encoding="latin-1"), expect_eom=True)))
        self.assertEqual(calls[3], call(
            TxMessage(bytes("\x01\xCA\x00\x00\x00\x00", encoding="latin-1"), expect_eom=False)))

        # Setup the mock with different sample numbers
        self.txrx.send_recv_message = MagicMock() #return_value=[(0x0139, 0x01000023), (0x0139, 0x02000023)])
        self.txrx.send_recv_message.side_effect = [[(0x01B2, 0x01000012)],
                                                   [(0x01B2, 0xABBABAC1)],
                                                   [(0x01B2, 0xABBABAC1)],
                                                   [(0x01B2, 0x02000013)]]
        mntrChannel = MonitoringChannel(self.txrx, self.channel_ini, self.settings)
        self.txrx.send_recv_message.reset_mock()
        value = mntrChannel.get_value()
        self.assertEquals(value.read_value, 19)

