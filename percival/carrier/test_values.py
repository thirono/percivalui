from __future__ import unicode_literals, absolute_import

import unittest, logging
from mock import MagicMock, call
from builtins import bytes

import percival.carrier.const as const
from percival.carrier.values import BoardValues
from percival.carrier.txrx import TxMessage


class TestBoardValuesClass(unittest.TestCase):
    def setUp(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(logging.DEBUG)
        self.txrx = MagicMock()
        self.txrx.send_recv_message = MagicMock()

    def TestFunctions(self):
        # Test reading values from carrier board
        self.value = BoardValues(self.txrx, const.BoardTypes.carrier)
        self.value.read_values()
        self.txrx.send_recv_message.assert_called_with(
            TxMessage(bytes("\x04\x02\x00\x00\x00\x00", encoding="latin-1"), num_response_msg=19, expect_eom=False))

        self.txrx.send_recv_message.reset_mock()
        # Test reading values from periphery left board
        self.value = BoardValues(self.txrx, const.BoardTypes.left)
        self.value.read_values()
        self.txrx.send_recv_message.assert_called_with(
            TxMessage(bytes("\x04\x00\x00\x00\x00\x00", encoding="latin-1"), num_response_msg=1, expect_eom=False))

        self.txrx.send_recv_message.reset_mock()
        # Test reading values from periphery bottom board
        self.value = BoardValues(self.txrx, const.BoardTypes.bottom)
        self.value.read_values()
        self.txrx.send_recv_message.assert_called_with(
            TxMessage(bytes("\x04\x01\x00\x00\x00\x00", encoding="latin-1"), num_response_msg=84, expect_eom=False))

        self.txrx.send_recv_message.reset_mock()
        # Test reading values from plugin board
        self.value = BoardValues(self.txrx, const.BoardTypes.plugin)
        self.value.read_values()
        self.txrx.send_recv_message.assert_called_with(
            TxMessage(bytes("\x04\x03\x00\x00\x00\x00", encoding="latin-1"), num_response_msg=1, expect_eom=False))

