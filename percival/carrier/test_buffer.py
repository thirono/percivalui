'''
Created on 17 July 2017

@author: gnx91527
'''

from __future__ import unicode_literals, absolute_import

import unittest, sys, logging
from mock import MagicMock, call
from builtins import bytes

import percival.carrier.const as const
from percival.carrier.buffer import BufferCommand, SensorBufferCommand
from percival.carrier.txrx import TxMessage


class TestBuffer(unittest.TestCase):

    def setUp(self):
        # Perform any setup here
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(logging.DEBUG)
        self.txrx = MagicMock()

    def TestSimpleBufferCommand(self):

        self.buffer = BufferCommand(self.txrx, const.BufferTarget.mezzanine_board_A)
        cmd = self.buffer._get_command_msg(const.BufferCmd.no_operation)
        self.assertEqual(cmd, TxMessage(bytes("\x03\x3B\x00\x00\x00\x00", encoding="latin-1"), expect_eom=False))

        cmd = self.buffer._get_command_msg(const.BufferCmd.read)
        self.assertEqual(cmd, TxMessage(bytes("\x03\x3B\x11\x00\x00\x00", encoding="latin-1"),
                                        num_response_msg=2,
                                        expect_eom=False))

        cmd = self.buffer._get_command_msg(const.BufferCmd.write, 0x5, 0x3A)
        self.assertEqual(cmd, TxMessage(bytes("\x03\x3B\x10\x05\x00\x3A", encoding="latin-1"),
                                        num_response_msg=2,
                                        expect_eom=False))

        self.txrx.send_recv_message = MagicMock(return_value=[(0x00000001, 0x00000002)])
        response = self.buffer.cmd_no_operation()
        self.assertEqual(response, [(0x00000001, 0x00000002)])

        self.txrx.send_recv_message = MagicMock(return_value=[(0x00000003, 0x00000004)])
        response = self.buffer.send_command(const.BufferCmd.write, 0x1, 0x2)
        self.assertEqual(response, [(0x00000003, 0x00000004)])

    def TestSensorBufferCommand(self):

        self.txrx.send_recv = MagicMock()
        self.txrx.send_recv_message = MagicMock(return_value=[(0x00000005, 0x00000006)])
        self.buffer = SensorBufferCommand(self.txrx)
        response = self.buffer.send_dacs_setup_cmd([0x00000001, 0x00000002, 0x00000003, 0x00000004])
        calls = self.txrx.send_recv.mock_calls
        # Assert that the data words were written into the buffer
        self.assertEqual(calls[0], call(bytes("\x02\xFA\x00\x00\x00\x01", encoding="latin-1"), None))
        self.assertEqual(calls[1], call(bytes("\x02\xFB\x00\x00\x00\x02", encoding="latin-1"), None))
        self.assertEqual(calls[2], call(bytes("\x02\xFC\x00\x00\x00\x03", encoding="latin-1"), None))
        self.assertEqual(calls[3], call(bytes("\x02\xFD\x00\x00\x00\x04", encoding="latin-1"), None))

        # Assert that the command response was es expected
        self.assertEqual(response, [(0x00000005, 0x00000006)])

