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
        #
        # Sensor DAC command
        #
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

        #
        # Sensor Config command
        #
        # Generate the words required to submit a sensor config command
        words = range(0,144)
        std_reply = (0xFFFF, 0xABBABAC1)
        sensor_reply = (0xFFF3, 0xABBA3333)
        # Create the returned expected responses for the config command
        return_values = []
        # Iteration 1 null command standard response
        return_values.append(std_reply)
        # Iteration 1 sensor response
        return_values.append([std_reply, sensor_reply])
        # Iteration 2 null command standard response
        return_values.append(std_reply)
        # Iteration 1 sensor response
        return_values.append([std_reply, sensor_reply])
        # Iteration 3 null command standard response
        return_values.append(std_reply)
        # Iteration 1 sensor response
        return_values.append([std_reply, sensor_reply])
        self.log.debug("Return values : %s", return_values)
        self.txrx.send_recv = MagicMock()
        self.txrx.send_recv_message = MagicMock()
        self.txrx.send_recv_message.side_effect = return_values
        self.buffer.send_configuration_setup_cmd(words)
        # Verify that the correct calls were made to the txrx object for filling in the buffers
        calls = self.txrx.send_recv.mock_calls
        # Assert that the data words were written into the buffer
        self.assertEqual(calls[0], call(bytes("\x02\xFA\x00\x00\x00\x00", encoding="latin-1"), None))
        self.assertEqual(calls[1], call(bytes("\x02\xFB\x00\x00\x00\x01", encoding="latin-1"), None))
        self.assertEqual(calls[2], call(bytes("\x02\xFC\x00\x00\x00\x02", encoding="latin-1"), None))
        self.assertEqual(calls[3], call(bytes("\x02\xFD\x00\x00\x00\x03", encoding="latin-1"), None))
        self.assertEqual(calls[4], call(bytes("\x02\xFE\x00\x00\x00\x04", encoding="latin-1"), None))
        self.assertEqual(calls[5], call(bytes("\x02\xFF\x00\x00\x00\x05", encoding="latin-1"), None))
        self.assertEqual(calls[6], call(bytes("\x03\x00\x00\x00\x00\x06", encoding="latin-1"), None))
        self.assertEqual(calls[7], call(bytes("\x03\x01\x00\x00\x00\x07", encoding="latin-1"), None))
        self.assertEqual(calls[8], call(bytes("\x03\x02\x00\x00\x00\x08", encoding="latin-1"), None))
        self.assertEqual(calls[9], call(bytes("\x03\x03\x00\x00\x00\x09", encoding="latin-1"), None))
        self.assertEqual(calls[70], call(bytes("\x03\x00\x00\x00\x00\x46", encoding="latin-1"), None))
        self.assertEqual(calls[71], call(bytes("\x03\x01\x00\x00\x00\x47", encoding="latin-1"), None))
        self.assertEqual(calls[72], call(bytes("\x03\x02\x00\x00\x00\x48", encoding="latin-1"), None))
        self.assertEqual(calls[73], call(bytes("\x03\x03\x00\x00\x00\x49", encoding="latin-1"), None))
        self.assertEqual(calls[74], call(bytes("\x03\x04\x00\x00\x00\x4A", encoding="latin-1"), None))
        self.assertEqual(calls[75], call(bytes("\x03\x05\x00\x00\x00\x4B", encoding="latin-1"), None))
        self.assertEqual(calls[76], call(bytes("\x03\x06\x00\x00\x00\x4C", encoding="latin-1"), None))
        self.assertEqual(calls[77], call(bytes("\x03\x07\x00\x00\x00\x4D", encoding="latin-1"), None))
        self.assertEqual(calls[78], call(bytes("\x03\x08\x00\x00\x00\x4E", encoding="latin-1"), None))
        self.assertEqual(calls[79], call(bytes("\x03\x09\x00\x00\x00\x4F", encoding="latin-1"), None))
        # Verify that the correct calls were made to the txrx object for sending the buffer commands
        calls = self.txrx.send_recv_message.mock_calls
        # Assert that the commands were sent in the correct order
        self.assertEqual(calls[0], call(TxMessage(bytes("\x03\x3B\x50\x00\x00\x00", encoding="latin-1"),
                                                  num_response_msg=1,
                                                  expect_eom=False)))
        self.assertEqual(calls[1], call(TxMessage(bytes("\x03\x3B\x51\x00\x00\x01", encoding="latin-1"),
                                                  num_response_msg=2,
                                                  expect_eom=False)))
        self.assertEqual(calls[2], call(TxMessage(bytes("\x03\x3B\x50\x00\x00\x00", encoding="latin-1"),
                                                  num_response_msg=1,
                                                  expect_eom=False)))
        self.assertEqual(calls[3], call(TxMessage(bytes("\x03\x3B\x51\x00\x00\x02", encoding="latin-1"),
                                                  num_response_msg=2,
                                                  expect_eom=False)))
        self.assertEqual(calls[4], call(TxMessage(bytes("\x03\x3B\x50\x00\x00\x00", encoding="latin-1"),
                                                  num_response_msg=1,
                                                  expect_eom=False)))
        self.assertEqual(calls[5], call(TxMessage(bytes("\x03\x3B\x51\x00\x00\x03", encoding="latin-1"),
                                                  num_response_msg=2,
                                                  expect_eom=False)))

