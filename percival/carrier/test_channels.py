'''
Created on 8 May 2015

@author: up45
'''
from __future__ import unicode_literals, absolute_import

import unittest, sys, logging
from mock import MagicMock
from builtins import bytes

import percival.carrier.const as const
from percival.carrier.channels import Channel, ControlChannel, MonitoringChannel
from percival.carrier.devices import DeviceFunction, DeviceCmd
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
        self.channel_ini.Component_family_ID = const.DeviceFamily.AD5629
        self.channel_ini.Board_type = const.BoardTypes.carrier
        ctrlChannel = ControlChannel(self.txrx, self.channel_ini, self.settings)
        # Verify the txrx mock had send_rcv_message called
        self.txrx.send_recv_message.assert_called_with(TxMessage(bytes("\x00\xF8\x00\x00\x00\x01", encoding="latin-1"), expect_eom=True))
