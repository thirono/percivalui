'''
Created on 19 May 2015

@author: Ulrik Pedersen
'''
from __future__ import print_function

import os, time, binascii, signal
import numpy, h5py

import logging
import sys
from percival.log import log

from percival.carrier.registers import UARTRegister, BoardRegisters, BoardTypes
from percival.carrier.devices import DeviceFunction, DeviceCmd, DeviceFamilyFeatures, DeviceFamily
from percival.carrier.txrx import TxRx, TxRxContext, hexify
from percival.configuration import ChannelParameters, ControlChannelIniParameters

board_ip_address = os.getenv("PERCIVAL_CARRIER_IP")


class ControlChannel:
    """
    Control a specific device channel on any of the control boards.
    """

    def __init__(self, txrx, channel_ini, settings):
        """ ControlChannel constructor.

        Keeps a reference to the txrx communication object and initialises itself based on the parameters in channel_ini.

        :param txrx: Percival communication context
        :type  txrx: TxRx
        :param channel_ini: Channel configuration parameters from INI file
        :type channel_ini: ControlChannelIniParameters
        """
#    def __init__(self, txrx, device_family, channel_index, uart_offset, settings, board):
#        '''Constructor
#
#            :param txrx: Percival communication context
#            :type  txrx: TxRx
#            :param device_family: The type of device
#            :type  device_family: DeviceFamily
#            :param channel_index: Control device channel index
#            :type  channel_index: int
#            :param settings: Control channel settings register map. The list can contain either integers data words
#                             or tuples of (addr, data).
#            :type  settings: list
#        '''
        #self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self.log = logging.getLogger(self.__class__.__name__)
        self._txrx = txrx
        self._channel_ini = channel_ini

        self.device_family = DeviceFamily(channel_ini.Component_family_ID)
        self._device_family_features = DeviceFamilyFeatures[self.device_family]

        if self._device_family_features.function != DeviceFunction.control:
            raise TypeError("Not a control device")
        self.channel_index = channel_ini._channel_number
        self.uart_device_address = channel_ini.UART_address

        self._reg_command = UARTRegister(0x00F8)
        self._reg_command.initialize_map([0,0,0])
        self._reg_command.fields.device_type = self._device_family_features.function.value
        self._reg_command.fields.device_index = self.channel_index

        self._reg_echo = UARTRegister(0x0139)

        addr_header, addr_control, addr_monitoring = BoardRegisters[BoardTypes(channel_ini.Board_type)]
        self._reg_control_settings = UARTRegister(addr_control)
        self._reg_control_settings.initialize_map(settings)
        self.log.debug("Control Settings Map: %s", self._reg_control_settings.fields)

        # Send an initialize command to the device
        self.cmd_initialize()

    def read_echo_word(self):
        self.log.debug("READ ECHO WORD")
        echo_cmd_msg = self._reg_echo.get_read_cmd_msg()
        response = self._txrx.send_recv_message(echo_cmd_msg)
        return response

    def get_command_msg(self, cmd):
        if not self._device_family_features.supports_cmd(cmd):
            raise TypeError("Device family does not support command %s"%cmd)
        self._reg_command.fields.device_cmd = cmd.value
        self.log.debug(self._reg_command.fields)
        cmd_msg = self._reg_command.get_write_cmd_msg(eom=True)[0]
        return cmd_msg

    def command(self, cmd):
        self.log.debug("Device Command: %s", cmd)
        cmd_msg = self.get_command_msg(cmd)
        response = self._txrx.send_recv_message(cmd_msg)
        return response

    def cmd_no_operation(self):
        result = self.command(DeviceCmd.no_operation)
        return result

    def cmd_set_and_get_value(self):
        result = self.command(DeviceCmd.set_and_get_value)
        return result

    def cmd_initialize(self):
        result = self.command(DeviceCmd.initialize)
        return result

    def cmd_control_set_value(self, value):
        self.log.debug("Device Control Settings write:")
        self._reg_control_settings.fields.value = value
        self.log.debug(self._reg_control_settings.fields)
        cmd_msg = self._reg_control_settings.get_write_cmd_msg(eom=True)
        self.log.debug(cmd_msg)
        # TODO: this is a bit hacky to go this far for the register index...
        value_register_index = self._reg_control_settings.fields._mem_map['value'].word_index
        response = self._txrx.send_recv_message(cmd_msg[value_register_index])
        return response

    def set_value(self, value):
        self.log.debug("set_value=%s", value)
        self.cmd_no_operation()
        self.cmd_control_set_value(value)
        self.cmd_no_operation()
        self.cmd_set_and_get_value()
        result = self.read_echo_word()
        return result[0][1]


class BoardSettings:
    def __init__(self, txrx, board):
        #self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self.log = logging.getLogger(self.__class__.__name__)
        self.txrx = txrx
        addr_header, addr_control, addr_monitoring = BoardRegisters[board]

        self._reg_control_settings = UARTRegister(addr_control)
        self._control_settings = None

    def readback_control_settings(self):
        self.log.debug("Readback Board Control Settings")
        cmd_msg = self._reg_control_settings.get_read_cmd_msg()
        response = self.txrx.send_recv_message(cmd_msg)
        self._control_settings = response

    def device_control_settings(self, device_index):
        result = self._control_settings[device_index:device_index+self._reg_control_settings.words_per_item]
        return result


if __name__ == '__main__':
    with TxRxContext(board_ip_address) as trx:
        ini_params = ChannelParameters("config/Channel parameters.ini")
        ini_params.load_ini()

        # Get the Control Channels
        log.debug("Control Channels: %s", str(ini_params.control_channels))
        log.debug("Monitoring Channels: %s", str(ini_params.monitoring_channels))
        log.debug("INI parameters: %s", ini_params)

        bs = BoardSettings(trx, BoardTypes.carrier)
        bs.readback_control_settings()

        cc_settings = bs.device_control_settings(0)
        log.info("Control Channel #2 settings from board: %s", hexify(cc_settings))

        vch0_ini = ini_params.control_channels_by_name("VCH0")
        log.info("vch0_ini: %s", vch0_ini)

        cc = ControlChannel(trx, vch0_ini, cc_settings)

        new_value = 5000
        log.info("Writing DAC channel 2 value = %d", new_value)
        time.sleep(0.2)
        echo_result = cc.set_value(new_value)
        if echo_result != new_value:
            log.warning("  Echo result does not match demanded value (%d != %d)", echo_result, new_value)
        else:
            log.info("  Echo result: %d", echo_result)

        new_value = 10000
        log.info("Writing DAC channel 2 value = %d", new_value)
        time.sleep(0.2)
        echo_result = cc.set_value(new_value)
        if echo_result != new_value:
            log.warning("  Echo result does not match demanded value (%d != %d)", echo_result, new_value)
        else:
            log.info("  Echo result: %d", echo_result)

        new_value = 0
        log.info("Writing DAC channel 2 value = %d", new_value)
        time.sleep(0.2)
        echo_result = cc.set_value(new_value)
        if echo_result != new_value:
            log.warning("  Echo result does not match demanded value (%d != %d)", echo_result, new_value)
        else:
            log.info("  Echo result: %d", echo_result)
