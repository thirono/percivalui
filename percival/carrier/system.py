"""
Created on 18 May 2016

:author: Alan Greer

A class representation for a Percival system command.

An instance is initialised with a percival.carrier.txrx.TxRx object and
commands can be sent using the send_command method.
"""
from __future__ import print_function

import logging
from percival.carrier import const
from percival.carrier.registers import UARTRegister


class SystemCommand(object):
    """
    Represent a Percival system command.
    """
    def __init__(self, txrx):
        """
        Constructor

        :param txrx: Percival communication context
        :type  txrx: TxRx
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self._txrx = txrx
        self._reg_command = UARTRegister(const.COMMAND)
        self._reg_command.initialize_map([0,0,0])

    def _get_command_msg(self, cmd):
        """
        Private method to construct a system command message object (TxMessage).

        The returned object contains the correct address and word for executing the
        specified command and can be sent through the txrx object to the Percival
        hardware.

        :param cmd: command to encode
        :type  cmd: SystemCmd
        :returns: percival.carrier.txrx.TxMessage
        """
        if type(cmd) != const.SystemCmd:
            raise TypeError("Command %s is not a SystemCommand"%cmd)
        self._reg_command.fields.system_cmd = cmd.value
        cmd_msg = self._reg_command.get_write_cmd_msg(eom=True)[2]
        return cmd_msg

    def _command(self, cmd):
        """
        Private method to construct and send a system command.

        This method gets the TxMessage object representation of the system command
        and sends it through the txrx object to the Percival hardware, returning any
        response.

        Returns nothing as the lower level checks for expected response.
        Can raise RuntimeError if the expected response is not received.

        :param cmd: command to encode
        :type  cmd: SystemCmd
        """
        cmd_msg = self._get_command_msg(cmd)
        self._txrx.send_recv_message(cmd_msg)

    def cmd_no_operation(self):
        """
        Method to send a no_operation system command.

        Returns nothing as the lower level checks for expected response.
        Can raise RuntimeError if the expected response is not received.
        """
        self._command(const.SystemCmd.no_operation)

    def send_command(self, cmd):
        """
        Method to send a system command.

        This method first sends a no_operation command, followed by the specified
        system command.

        :param cmd: command to encode
        :type  cmd: SystemCmd
        """
        self.cmd_no_operation()
        self._command(cmd)

