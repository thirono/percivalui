'''
Created on 18 May 2016

@author: gnx91527
'''
from __future__ import print_function

import logging

from percival.carrier import const
from percival.carrier.registers import UARTRegister


class BufferCommand(object):
    """
    Represent a buffer command.
    """
    def __init__(self, txrx, target):
        self._log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self._txrx = txrx
        self._target = target
        self._reg_command = UARTRegister(const.COMMAND)
        self._reg_command.initialize_map([0,0,0])

    def _get_command_msg(self, cmd, words=None, address=None):
        if cmd == const.BufferCmd.no_operation:
            self._reg_command.fields.buffer_cmd = 0
            self._reg_command.fields.buffer_cmd_destination = 0
            self._reg_command.fields.buffer_cmd_words = 0
            self._reg_command.fields.buffer_cmd_address = 0
        else:
            self._reg_command.fields.buffer_cmd_destination = self._target.value
            self._reg_command.fields.buffer_cmd = const.BufferCommands[self._target][cmd]["command"]
            if words:
                self._reg_command.fields.buffer_cmd_words = words
            else:
                self._reg_command.fields.buffer_cmd_words = 0
            if address:
                self._reg_command.fields.buffer_cmd_address = address
            else:
                self._reg_command.fields.buffer_cmd_address = 0

        cmd_msg = self._reg_command.get_write_cmd_msg(eom=False)[1]
        cmd_msg.num_response_msg = const.BufferCommands[self._target][cmd]["response"]
        return cmd_msg

    def _command(self, cmd, words=None, address=None):
        cmd_msg = self._get_command_msg(cmd, words, address)
        self._log.critical("Command Message: %s", cmd_msg)
        response = self._txrx.send_recv_message(cmd_msg)
        self._log.critical("Response Message: %s", response)
        return response

    def cmd_no_operation(self):
        result = self._command(const.BufferCmd.no_operation)
        return result

    def send_command(self, cmd, words, address):
        self.cmd_no_operation()
        self._command(cmd, words, address)

