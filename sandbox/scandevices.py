'''
Created on 19 May 2015

@author: Ulrik Pedersen
'''
from __future__ import print_function

import os, time

import logging
from percival.log import log

from percival.carrier import const
from percival.carrier.registers import UARTRegister, BoardRegisters, generate_register_maps
from percival.carrier.devices import DeviceFunction, DeviceCmd, DeviceFamilyFeatures, DeviceFamily
from percival.carrier.txrx import TxRx, TxRxContext, hexify
from percival.configuration import ChannelParameters, ControlChannelIniParameters

board_ip_address = os.getenv("PERCIVAL_CARRIER_IP")


class ControlChannel:
    """
    Control a specific device channel on any of the control boards.
    """

    def __init__(self, txrx, channel_ini, settings):
        """ ControlChannelMap constructor.

        Keeps a reference to the txrx communication object and initialises itself based on the parameters in channel_ini.

        :param txrx: Percival communication context
        :type  txrx: TxRx
        :param channel_ini: Channel configuration parameters from INI file
        :type channel_ini: ControlChannelIniParameters
        """
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

        self._reg_command = UARTRegister(const.COMMAND)
        self._reg_command.initialize_map([0,0,0])
        self._reg_command.fields.device_type = self._device_family_features.function.value
        self._reg_command.fields.device_index = self.channel_index

        self._reg_echo = UARTRegister(const.READ_ECHO_WORD)

        addr_header, addr_control, addr_monitoring = BoardRegisters[const.BoardTypes(channel_ini.Board_type)]
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
        self.log.debug("Device CommandMap: %s", cmd)
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

    def set_value(self, value, timeout=0.1):
        self.log.debug("set_value=%s (\"%s\")", value, self._channel_ini.Channel_name)
        self.cmd_no_operation()
        self.cmd_control_set_value(value)
        self.cmd_no_operation()
        self.cmd_set_and_get_value()
        start_time = time.time()
        while True:
            echo = self.read_echo_word()
            result = generate_register_maps(echo)
            if result[0].i2c_communication_error:
                raise IOError("I2C communication error when writing to %s", self._channel_ini.Channel_name)
            if result[0].read_value == value:
                break
            if time.time() > (start_time + timeout):
                raise RuntimeError("Timeout when reading back value from ECHO word")

            # skip the retry!
            # TODO: fix the retry feature - it doesn't work properly and always times out
            break

            time.sleep(0.1)
            log.debug("####### Retrying reading ECHO word. Got: %s", result)
        return result[0]


class BoardSettings:
    def __init__(self, txrx, board):
        #self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self.log = logging.getLogger(self.__class__.__name__)
        self.txrx = txrx
        header_block, control_block, monitoring_block = BoardRegisters[board]

        self._reg_control_settings = UARTRegister(control_block)
        self._control_settings = None

        self._reg_monitoring_settings = UARTRegister(monitoring_block)
        self._monitoring_settings = None

    def _readback_settings(self, uart_register):
        cmd_msg = uart_register.get_read_cmd_msg()
        response = self.txrx.send_recv_message(cmd_msg)
        return response

    def readback_control_settings(self):
        self.log.debug("Readback Board Control Settings")
        self._control_settings = self._readback_settings(self._reg_control_settings)

    def device_control_settings(self, device_index):
        result = self._control_settings[device_index:device_index+self._reg_control_settings.words_per_item]
        return result

    def readback_monitoring_settings(self):
        self.log.debug("Readback Board Monitoring Settings")
        self._monitoring_settings = self._readback_settings(self._reg_monitoring_settings)


def read_carrier_monitors(txrx):
    uart_block = UARTRegister(const.READ_VALUES_CARRIER)
    cmd_msg = uart_block.get_read_cmd_msg()
    response = txrx.send_recv_message(cmd_msg)
    read_maps = generate_register_maps(response)
    return read_maps

if __name__ == '__main__':
    with TxRxContext(board_ip_address) as trx:
        ini_params = ChannelParameters("config/Channel parameters.ini")
        ini_params.load_ini()

        # Get the Control Channels
        log.debug("Control Channels: %s", str(ini_params.control_channels))
        log.debug("Monitoring Channels: %s", str(ini_params.monitoring_channels))
        log.debug("INI parameters: %s", ini_params)

        bs = BoardSettings(trx, const.BoardTypes.carrier)
        bs.readback_control_settings()

        # TODO: it should not be necessary to hardcode the index 0 here
        cc_settings = bs.device_control_settings(0)
        log.info("Control Channel #2 settings from board: %s", hexify(cc_settings))

        vch0_ini = ini_params.control_channels_by_name("VCH0")
        log.info("vch0_ini: %s", vch0_ini)

        cc = ControlChannel(trx, vch0_ini, cc_settings)

        new_value = 5000
        log.info("Writing DAC channel 2 value = %d", new_value)
        echo_result = cc.set_value(new_value, timeout=1.0)
        log.info("ECHO: %s", echo_result)
        if echo_result.read_value != new_value:
            log.warning("  Echo result does not match demanded value (%d != %d)", echo_result.read_value, new_value)
        adcs = read_carrier_monitors(trx)
        log.info("Read carrier monitoring channels: %s", adcs[:-3])
        channels = [(dac.sample_number, dac.read_value) for dac in adcs]
        log.info("  ADCs: %s", channels)

        new_value = 10000
        log.info("Writing DAC channel 2 value = %d", new_value)
        echo_result = cc.set_value(new_value, timeout=1.0)
        log.info("ECHO: %s", echo_result)
        if echo_result.read_value != new_value:
            log.warning("  Echo result does not match demanded value (%d != %d)", echo_result.read_value, new_value)
        adcs = read_carrier_monitors(trx)
        log.info("Read carrier monitoring channels: %s", adcs[:-3])
        channels = [(dac.sample_number, dac.read_value) for dac in adcs]
        log.info("  ADCs: %s", channels)

        new_value = 0
        log.info("Writing DAC channel 2 value = %d", new_value)
        echo_result = cc.set_value(new_value, timeout=1.0)
        log.info("ECHO: %s", echo_result)
        if echo_result.read_value != new_value:
            log.warning("  Echo result does not match demanded value (%d != %d)", echo_result.read_value, new_value)
        adcs = read_carrier_monitors(trx)
        log.info("Read carrier monitoring channels: %s", adcs[:-3])
        channels = [(dac.sample_number, dac.read_value) for dac in adcs]
        log.info("  ADCs: %s", channels)
