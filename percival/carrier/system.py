'''
Created on 18 May 2016

@author: gnx91527
'''
from __future__ import print_function

import logging
from percival.log import log

from percival.carrier import const
from percival.carrier.registers import UARTRegister

class SystemCommand(object):
    """
    Represent a system command.
    """
    def __init__(self, txrx):
        self.log = logging.getLogger(self.__class__.__name__)
        self._txrx = txrx
        self._reg_command = UARTRegister(const.COMMAND)
        self._reg_command.initialize_map([0,0,0])

    def _get_command_msg(self, cmd):
        if type(cmd) != const.SystemCmd:
            raise TypeError("Command %s is not a SystemCommand"%cmd)
        self._reg_command.fields.system_cmd = cmd.value
        cmd_msg = self._reg_command.get_write_cmd_msg(eom=True)[2]
        return cmd_msg

    def _command(self, cmd):
        cmd_msg = self._get_command_msg(cmd)
        response = self._txrx.send_recv_message(cmd_msg)
        return response

    def cmd_no_operation(self):
        result = self._command(const.SystemCmd.no_operation)
        return result

    def send_command(self, cmd):
        self.cmd_no_operation()
        self._command(cmd)

