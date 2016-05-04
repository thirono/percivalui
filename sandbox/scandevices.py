'''
Created on 19 May 2015

@author: Ulrik Pedersen
'''
from __future__ import print_function

import os, time
from collections import OrderedDict

import logging
from percival.log import log

from percival.carrier import const
from percival.carrier.registers import UARTRegister, BoardRegisters, generate_register_maps
from percival.carrier.devices import DeviceFunction, DeviceCmd, DeviceFamilyFeatures, DeviceFamily
from percival.carrier.txrx import TxRx, TxRxContext, hexify
from percival.configuration import ChannelParameters, ControlChannelIniParameters

board_ip_address = os.getenv("PERCIVAL_CARRIER_IP")


class Channel(object):
    """
    Represent a specific device channel on any of the control boards.
    """

    def __init__(self, txrx, channel_ini, settings):
        """ Channel constructor. Call this from derived classes

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

        self._addr_settings_header, self._addr_settings_control, self._addr_settings_monitoring = \
            BoardRegisters[const.BoardTypes(channel_ini.Board_type)]

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


class ControlChannel(Channel):
    def __init__(self, txrx, channel_ini, settings):
        super(ControlChannel, self).__init__(txrx, channel_ini, settings)

        self._reg_control_settings = UARTRegister(self._addr_settings_control)
        self._reg_control_settings.initialize_map(settings)
        self.log.debug("Control Settings Map: %s", self._reg_control_settings.fields)

        # Send an initialize command to the device
        self.cmd_initialize()

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


class MonitoringChannel(Channel):
    def __init__(self, txrx, channel_ini, settings):
        super(MonitoringChannel, self).__init__(txrx, channel_ini, settings)

        self._reg_monitor_settings = UARTRegister(self._addr_settings_monitoring)
        self._reg_monitor_settings.initialize_map(settings)
        self.log.debug("Monitor Settings Map: %s", self._reg_monitor_settings.fields)


class BoardSettings:
    def __init__(self, txrx, board):
        #self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self.log = logging.getLogger(self.__class__.__name__)
        self.txrx = txrx
        self._header_block, self._control_block, self._monitoring_block = BoardRegisters[board]

        self._reg_control_settings = UARTRegister(self._control_block)
        self._control_settings = None

        self._reg_monitoring_settings = UARTRegister(self._monitoring_block)
        self._monitoring_settings = None

    def _readback_settings(self, uart_register):
        cmd_msg = uart_register.get_read_cmd_msg()
        response = self.txrx.send_recv_message(cmd_msg)
        return response

    def readback_control_settings(self):
        self.log.debug("Readback Board Control Settings")
        self._control_settings = self._readback_settings(self._reg_control_settings)

    def device_control_settings(self, device_addr):
        offset = device_addr - self._control_block.start_address
        if not self._control_block.is_address_valid(device_addr):
            raise IndexError("Device address 0x%X not in range of block 0x%X" %
                             (device_addr, self._control_block.start_address))
        result = self._control_settings[offset:offset+self._reg_control_settings.words_per_item]
        return result

    def readback_monitoring_settings(self):
        self.log.debug("Readback Board Monitoring Settings")
        self._monitoring_settings = self._readback_settings(self._reg_monitoring_settings)


class ReadMonitors(object):
    def __init__(self, txrx, uart_block, ini_params):
        """

        :param txrx:
        :param uart_block:
        :type: :obj:`percival.carrier.const.UARTBlock`
        """
        self._txrx = txrx
        self._uart_block = uart_block
        self._uart_register_block = UARTRegister(uart_block)
        self._cmd_msg = self._uart_register_block.get_read_cmd_msg()
        self._channel_data = OrderedDict()
        self._set_channel_names(ini_params)


    def _set_channel_names(self, ini_params):
        response = self._txrx.send_recv_message(self._cmd_msg)
        self._channel_names = []
        for addr, value in response:
            index = addr - self._uart_block.start_address
            #      addr is just a READ VALUES register address - not the channels base address.
            name = ini_params.monitoring_channel_name_by_index(index)
            self._channel_data.update({name: []})


    def read_carrier_monitors(self):
        """Read all carrier monitor channels with one READ VALUES shortcut command

        Parse the resuling [(address, data), (address, data)...] array of tuples into a list of
        :class:`percival.carrier.register.ReadValueMap` objects.

        :returns: list of :class:`percival.carrier.register.ReadValueMap` objects.
        :rtype: list
        """
        response = self._txrx.send_recv_message(self._cmd_msg)
        read_maps = generate_register_maps(response)
        result = dict(zip(self._channel_data.keys(), read_maps))
        for name, value in result.items():
            self._channel_data[name].append(value)
        return result

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

        vch0_ini = ini_params.control_channels_by_name("VCH0")
        log.info("vch0_ini: %s", vch0_ini)

        cc_settings = bs.device_control_settings(vch0_ini.UART_address)
        log.info("Control Channel #2 settings from board: %s", hexify(cc_settings))

        cc = ControlChannel(trx, vch0_ini, cc_settings)

        readmon = ReadMonitors(trx, const.READ_VALUES_CARRIER, ini_params)

        for new_value in [5000, 10000, 30000, 0]:
            log.info("Writing DAC channel 2 value = %d", new_value)
            echo_result = cc.set_value(new_value, timeout=1.0)
            log.info("ECHO: %s", echo_result)
            if echo_result.read_value != new_value:
                log.warning("  Echo result does not match demanded value (%d != %d)", echo_result.read_value, new_value)
            adcs = readmon.read_carrier_monitors()
            log.info("Read carrier monitoring channels: %s", adcs.keys())

        log.info(readmon._channel_data)

