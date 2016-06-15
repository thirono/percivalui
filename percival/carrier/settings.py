'''
Created on 10 June 2016

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

class BoardSettings:
    def __init__(self, txrx, board):
        self.log = logging.getLogger(self.__class__.__name__)
        self.txrx = txrx
        self.board = board
        self._header_block, self._control_block, self._monitoring_block = BoardRegisters[board]

        self._reg_header_settings = UARTRegister(self._header_block)

        self._reg_control_settings = UARTRegister(self._control_block)
        self._control_settings = None

        self._reg_monitoring_settings = UARTRegister(self._monitoring_block)
        self._monitoring_settings = None

    def initialise_board(self, ini):
        # Create the settings message
        self._reg_header_settings.fields.eeprom_address = 0x50
        self._reg_header_settings.fields.monitoring_channels_count = ini.monitoring_channels_count(self.board)
        self._reg_header_settings.fields.control_channels_count = ini.control_channels_count(self.board)
        cmd_msg = self._reg_header_settings.get_write_cmd_msg(True)

        # Initialise the control channels
        #self.log.info(self._reg_control_settings.num_items)
        self._control_settings = {}
        for address in range(0, self._reg_control_settings.num_items):
            channel_address = self._reg_control_settings._uart_address + (address * self._reg_control_settings.words_per_item)
            channel = ini.control_channel_by_address(channel_address)
            #self.log.info(channel)
            #self.log.info("Uart address %02X", self._reg_control_settings._uart_address + (address * self._reg_control_settings.words_per_item))
            #self.log.info(channel.Channel_ID)

            self._control_settings[address] = UARTRegister(self._control_block, channel_address)

            self._control_settings[address].fields.channel_id = channel.Channel_ID
            self._control_settings[address].fields.device_address = 0
            self._control_settings[address].fields.board_type = channel.Board_type
            self._control_settings[address].fields.component_family_id = channel.Component_family_ID
            self._control_settings[address].fields.device_i2c_bus_select = channel.I2C_bus_selection
            self._control_settings[address].fields.channel_device_id = channel.Device_ID
            self._control_settings[address].fields.channel_sub_address = channel.I2C_Sub_address
            self._control_settings[address].fields.device_address = channel.I2C_address
            self._control_settings[address].fields.channel_range_max = channel.Maximum_value
            self._control_settings[address].fields.channel_range_min = channel.Minimum_value
            self._control_settings[address].fields.channel_default_on = channel.Default_ON_value
            self._control_settings[address].fields.channel_default_off = channel.Default_OFF_value
            self._control_settings[address].fields.power_status = channel.Power_status
            self._control_settings[address].fields.value = channel.Value
            cmd_msg += self._control_settings[address].get_write_cmd_msg(True)

        # Initialise the control channels
        # self.log.info(self._reg_control_settings.num_items)
        self._monitoring_settings = {}
        for address in range(0, self._reg_monitoring_settings.num_items):
            channel_address = self._reg_monitoring_settings._uart_address + (address * self._reg_monitoring_settings.words_per_item)
            channel = ini.monitoring_channel_by_address(channel_address)
            #self.log.info(channel_address)
            # self.log.info("Uart address %02X", self._reg_control_settings._uart_address + (address * self._reg_control_settings.words_per_item))
            # self.log.info(channel.Channel_ID)

            self._monitoring_settings[address] = UARTRegister(self._monitoring_block, channel_address)

            #self.log.info("Channel ID: %d", channel.Channel_ID)
            self._monitoring_settings[address].fields.channel_id = channel.Channel_ID
            self._monitoring_settings[address].fields.device_address = 0
            self._monitoring_settings[address].fields.board_type = channel.Board_type
            self._monitoring_settings[address].fields.component_family_id = channel.Component_family_ID
            self._monitoring_settings[address].fields.device_i2c_bus_select = channel.I2C_bus_selection
            self._monitoring_settings[address].fields.channel_device_id = channel.Device_ID
            self._monitoring_settings[address].fields.channel_sub_address = channel.I2C_Sub_address
            self._monitoring_settings[address].fields.device_address = channel.I2C_address
            self._monitoring_settings[address].fields.channel_ext_low_threshold = channel.Extreme_low_threshold
            self._monitoring_settings[address].fields.channel_ext_high_threshold = channel.Extreme_high_threshold
            self._monitoring_settings[address].fields.channel_low_threshold = channel.Low_threshold
            self._monitoring_settings[address].fields.channel_high_threshold = channel.High_threshold
            self._monitoring_settings[address].fields.channel_monitoring = channel.Monitoring
            self._monitoring_settings[address].fields.safety_exception_threshold = channel.Safety_exception_threshold
            self._monitoring_settings[address].fields.read_frequency = channel.Read_frequency
            cmd_msg += self._monitoring_settings[address].get_write_cmd_msg(True)

        return cmd_msg

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

    def device_monitoring_settings(self, device_addr):
        offset = device_addr - self._monitoring_block.start_address
        if not self._monitoring_block.is_address_valid(device_addr):
            raise IndexError("Device address 0x%X not in range of block 0x%X" %
                             (device_addr, self._monitoring_block.start_address))
        result = self._monitoring_settings[offset:offset+self._reg_monitoring_settings.words_per_item]
        return result

    def readback_monitoring_settings(self):
        self.log.debug("Readback Board Monitoring Settings")
        self._monitoring_settings = self._readback_settings(self._reg_monitoring_settings)

