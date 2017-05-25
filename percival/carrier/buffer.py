'''
Created on 15 July 2016

:author: Alan Greer

A class representation for a Percival buffer command.

An instance is initialised with a percival.carrier.txrx.TxRx object and
also the target destination for commands (const.BufferTarget).  Commands
can then be constructed and sent depending on the target.  Commands can
be sent using the send_command method.

TODO: This assumes the buffer has already been filled with values.  This
class could instead of taking the number of words, take the actual words and
fill the buffer itself.
'''
from __future__ import print_function

import logging

from percival.carrier import const
from percival.carrier.encoding import encode_multi_message
from percival.carrier.registers import UARTRegister


class BufferCommand(object):
    """
    Represent a Percival buffer command.
    """
    def __init__(self, txrx, target):
        """
        Constructor

        :param txrx: Percival communication context
        :type  txrx: TxRx
        :param target: target board for the buffer command
        :type  target: BufferTarget
        """
        self._log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self._txrx = txrx
        self._target = target
        self._reg_command = UARTRegister(const.COMMAND)
        self._reg_command.initialize_map([0,0,0])

    def _get_command_msg(self, cmd, words=None, address=None):
        """
        Private method to construct a buffer command message object (TxMessage).

        The returned object contains the correct address and word for executing the
        specified command and can be sent through the txrx object to the Percival
        hardware.

        Depending on the target the command value can take on different meanings, and
        also the number of return messages can vary.  These values are looked up from
        the percival.carrier.const.BufferCommands dictionary.

        :param cmd: command to encode
        :type  cmd: BufferCmd
        :param words: the number of words in the buffer to execute the command on
        :param address: the starting address of the target to execute the command on
        :returns: percival.carrier.txrx.TxMessage
        """
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
        """
        Private method to construct and send a buffer command.

        This method gets the TxMessage object representation of the buffer command
        and sends it through the txrx object to the Percival hardware, returning any
        response.

        :param cmd: command to encode
        :type  cmd: BufferCmd
        :param words: the number of words in the buffer to execute the command on
        :param address: the starting address of the target to execute the command on
        :returns: list of (address, dataword) tuples
        """
        cmd_msg = self._get_command_msg(cmd, words, address)
        self._log.critical("Command Message: %s", cmd_msg)
        response = self._txrx.send_recv_message(cmd_msg)
        self._log.critical("Response Message: %s", response)
        return response

    def cmd_no_operation(self):
        """
        Method to send a no_operation buffer command.

        :returns: list of (address, dataword) tuples
        """
        result = self._command(const.BufferCmd.no_operation)
        return result

    def send_command(self, cmd, words, address):
        """
        Method to send a buffer command.

        This method first sends a no_operation command, followed by the specified
        buffer command.

        :param cmd: command to encode
        :type  cmd: BufferCmd
        :param words: the number of words in the buffer to execute the command on
        :param address: the starting address of the target to execute the command on
        """
        self.cmd_no_operation()
        self._command(cmd, words, address)


class SensorBufferCommand(BufferCommand):
    def __init__(self, txrx):
        super(SensorBufferCommand, self).__init__(txrx, const.BufferTarget.percival_sensor)
        self._log = logging.getLogger(".".join([__name__, self.__class__.__name__]))

    def send_dacs_setup_cmd(self, words):
        # First encode the words into the correct message format and send the values
        # to fill up the buffer
        msg = encode_multi_message(const.WRITE_BUFFER.start_address, words)
        self._log.debug("Writing buffer DAC values to address: %X ...", const.WRITE_BUFFER.start_address)
        try:
            for item in msg:
                self._txrx.send_recv(item, None)
        except RuntimeError:
            self._log.exception("No response (addr: %X)", const.WRITE_BUFFER.start_address)

        # Now send the command to write the buffer as sensor DAC values
        # cmd = send_DACs_setup_to_target
        # words = 0
        # address = 1
        self.send_command(const.BufferCmd.write, 0, 1)
