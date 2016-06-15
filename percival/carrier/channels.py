'''
Created on 16 May 2016

@author: gnx91527
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
        self.log = logging.getLogger(self.__class__.__name__)
        self._txrx = txrx
        self._channel_ini = channel_ini

        self.device_family = DeviceFamily(channel_ini.Component_family_ID)
        self._device_family_features = DeviceFamilyFeatures[self.device_family]

#        if self._device_family_features.function != DeviceFunction.control:
#            raise TypeError("Not a control device")
        self.channel_index = channel_ini._channel_number
        self.log.debug("Channel index number: %d", self.channel_index)
        self.uart_device_address = channel_ini.UART_address
        self.log.debug("Channel device address: %d", self.uart_device_address)

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
        self.log.debug("Device CommandMsg: %s", cmd_msg)
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
    """ ControlChannel constructor. Create a control channel

    Keeps a reference to the txrx communication object and initialises itself based on the parameters in channel_ini.
    Provides the set_value method in addition to the general channel methods

    :param txrx: Percival communication context
    :type  txrx: TxRx
    :param channel_ini: Channel configuration parameters from INI file
    :type channel_ini: ControlChannelIniParameters
    :param settings: List of values used to initialise UARTRegister
    :type settings: List
    """
    def __init__(self, txrx, channel_ini, settings):
        super(ControlChannel, self).__init__(txrx, channel_ini, settings)

        # Setup this control channels UART register
        # _addr_settings_control is a UARTBlock obtained from BoardRegisters
        # uart_device_address is read from the channel ini object for this channel
        self._reg_control_settings = UARTRegister(self._addr_settings_control, self.uart_device_address)
        # Initialise the UARTRegister map
        self._reg_control_settings.initialize_map(settings)
        self.log.debug("Control Settings Map: %s", self._reg_control_settings.fields)

        # Send an initialize command to the device if it is supported
        if self._device_family_features.supports_cmd(DeviceCmd.initialize):
            self.cmd_initialize()

    def cmd_control_set_value(self, value):
        self.log.debug("Device Control Settings write:")
        self._reg_control_settings.fields.value = value
        # Check if the control device is a potentiometer
        if self.device_family == DeviceFamily.AD5242 or self.device_family == DeviceFamily.AD5263:
            # This type of device requires power status set to on (1)
            self._reg_control_settings.fields.power_status = 1
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
                self.log.debug("Read value same a set value %s (\"%s\")", value, self._channel_ini.Channel_name)
                break
            if time.time() > (start_time + timeout):
                raise RuntimeError("Timeout when reading back value from ECHO word")

            # skip the retry!
            # TODO: fix the retry feature - it doesn't work properly and always times out
            #break

            time.sleep(0.1)
            log.debug("####### Retrying reading ECHO word. Got: %s", result)
        return result[0]


class MonitoringChannel(Channel):
    def __init__(self, txrx, channel_ini, settings):
        super(MonitoringChannel, self).__init__(txrx, channel_ini, settings)

        self._reg_monitor_settings = UARTRegister(self._addr_settings_monitoring)
        self._reg_monitor_settings.initialize_map(settings)
        log.debug("Monitor Settings Map: %s", self._reg_monitor_settings.fields)

    def get_value(self, timeout=0.1):
        log.debug("get_value (\"%s\")", self._channel_ini.Channel_name)
        # We need to store the sample number from the last write
        echo = self.read_echo_word()
        result = generate_register_maps(echo)
        sample_number = result[0].sample_number
        log.debug("Initial sample_number %s", sample_number)
        self.cmd_no_operation()
        self.cmd_set_and_get_value()
        start_time = time.time()
        while True:
            echo = self.read_echo_word()
            # Although this is a readout of the echo word, for monitors it provides
            # status as though it was a read value
            result = generate_register_maps(echo)
            if result[0].i2c_communication_error:
                raise IOError("I2C communication error when writing to %s", self._channel_ini.Channel_name)
            if result[0].sample_number != sample_number:
                log.debug("Sample number has changed %s", result[0].sample_number)
                break
            if time.time() > (start_time + timeout):
                raise RuntimeError("Timeout when reading back value from ECHO word")

            # skip the retry!
            # TODO: fix the retry feature - it doesn't work properly and always times out
            #break

            time.sleep(0.1)
            log.debug("####### Retrying reading ECHO word. Got: %s", result)

        log.debug("got value=%s (\"%s\")", result[0], self._channel_ini.Channel_name)
        return result[0]

