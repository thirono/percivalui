'''
Created on 10 June 2016

@author: gnx91527
'''
from __future__ import print_function

import os, time

import logging
from percival.log import log

from percival.carrier.registers import UARTRegister, BoardValueRegisters, generate_register_maps

class BoardValues:
    def __init__(self, txrx, board):
        self.log = logging.getLogger(self.__class__.__name__)
        self._txrx = txrx
        self._board = board
        self._value_block = BoardValueRegisters[board]
        self._reg_monitoring_values = UARTRegister(self._value_block)
        self._cmd_msg = self._reg_monitoring_values.get_read_cmd_msg()


    def read_values(self):
        """Read all carrier monitor channels with one READ VALUES shortcut command

        Parse the resuling [(address, data), (address, data)...] array of tuples into a list of
        :class:`percival.carrier.register.ReadValueMap` objects.

        :returns: list of :class:`percival.carrier.register.ReadValueMap` objects.
        :rtype: list
        """
        response = self._txrx.send_recv_message(self._cmd_msg)
        read_maps = generate_register_maps(response)
        #result = dict(zip(self._channel_data.keys(), read_maps))
        return response
