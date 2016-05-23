'''
Created on 20 May 2016

@author: Alan Greer
'''
from __future__ import print_function
from future.utils import raise_with_traceback

import os, time
import argparse

import logging
from percival.log import log

import os
from collections import OrderedDict
from configparser import SafeConfigParser
from percival.carrier.encoding import (encode_message, encode_multi_message, decode_message)

from percival.carrier import const
from percival.carrier.registers import UARTRegister, BoardRegisters, generate_register_maps
from percival.carrier.txrx import TxRx, TxRxContext, hexify
from percival.configuration import find_file, ChannelParameters, ControlChannelIniParameters

board_ip_address = os.getenv("PERCIVAL_CARRIER_IP")

class BoardSettings:
    def __init__(self, txrx, board):
        #self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
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

    def readback_monitoring_settings(self):
        self.log.debug("Readback Board Monitoring Settings")
        self._monitoring_settings = self._readback_settings(self._reg_monitoring_settings)


class PercivalParameters(object):
    def __init__(self):
        self._board_params = {
            const.BoardTypes.left: BoardParameters("config/Board LEFT.ini"),
            const.BoardTypes.bottom: BoardParameters("config/Board BOTTOM.ini"),
            const.BoardTypes.carrier: BoardParameters("config/Board CARRIER.ini"),
            const.BoardTypes.plugin: BoardParameters("config/Board PLUGIN.ini")
        }
        self._channel_params = ChannelParameters("config/Channel parameters.ini")

    def load_ini(self):
        self._board_params[const.BoardTypes.left].load_ini()
        self._board_params[const.BoardTypes.bottom].load_ini()
        self._board_params[const.BoardTypes.carrier].load_ini()
        self._board_params[const.BoardTypes.plugin].load_ini()
        self._channel_params.load_ini()
        #log.info(self._channel_params.control_channels)


    def board_name(self, type):
        return self._board_params[type].board_name

    def board_type(self, type):
        return self._board_params[type].board_type

    def control_channels_count(self, type):
        return self._board_params[type].control_channels_count

    def monitoring_channels_count(self, type):
        return self._board_params[type].monitoring_channels_count

    def control_channel_by_address(self, uart_address):
        return self._channel_params.control_channel_by_address(uart_address)

    def monitoring_channel_by_address(self, uart_address):
        return self._channel_params.monitoring_channel_by_address(uart_address)


class BoardParameters(object):
    """
    Loads device channel settings and parameters from an INI file.
    """
    def __init__(self, ini_file):
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self.log.setLevel(logging.DEBUG)
        self._ini_filename = find_file(ini_file)
        self.conf = None


    def load_ini(self):
        """
        Loads and parses the data from INI file. The data is stored internally in the object and can be retrieved
        through the `self.control_channels` and `self.monitoring_channels` properties.
        """
        self._control_channels = None
        self._monitoring_channels = None
        self.conf = SafeConfigParser(dict_type=OrderedDict)
        self.conf.read(self._ini_filename)

        #for section in self.conf.sections():
        #    log.info(str(section))

    @property
    def board_name(self):
        if "Board_header" not in self.conf.sections():
            raise_with_traceback(RuntimeError("Board_header section not found in ini file %s" % str(self._ini_filename)))
        return self.conf.get("Board_header", "Board_name")

    @property
    def board_type(self):
        if "Board_header" not in self.conf.sections():
            raise_with_traceback(RuntimeError("Board_header section not found in ini file %s" % str(self._ini_filename)))
        return const.BoardTypes(self.conf.getint("Board_header", "Board_type"))


    @property
    def board_revision(self):
        if "Board_header" not in self.conf.sections():
            raise_with_traceback(RuntimeError("Board_header section not found in ini file %s" % str(self._ini_filename)))
        return self.conf.getint("Board_header", "Board_revision_number")

    @property
    def control_channels_count(self):
        if "Entry_counts" not in self.conf.sections():
            raise_with_traceback(RuntimeError("Entry_counts section not found in ini file %s" % str(self._ini_filename)))
        return self.conf.getint("Entry_counts", "Control_channels_count")


    @property
    def monitoring_channels_count(self):
        if "Entry_counts" not in self.conf.sections():
            raise_with_traceback(RuntimeError("Entry_counts section not found in ini file %s" % str(self._ini_filename)))
        return self.conf.getint("Entry_counts", "Monitoring_channels_count")

class PercivalBoard(object):
    def __init__(self, txrx):
        self._txrx = txrx
        self._percival_params = PercivalParameters()
        self._board_settings_left = BoardSettings(txrx, const.BoardTypes.left)
        self._board_settings_bottom = BoardSettings(txrx, const.BoardTypes.bottom)
        self._board_settings_carrier = BoardSettings(txrx, const.BoardTypes.carrier)
        self._board_settings_plugin = BoardSettings(txrx, const.BoardTypes.plugin)

    def load_ini(self):
        self._percival_params.load_ini()

    def initialise_board(self):
        self.load_ini()
        cmd_msgs = self._board_settings_left.initialise_board(self._percival_params)
        cmd_msgs += self._board_settings_bottom.initialise_board(self._percival_params)
        cmd_msgs += self._board_settings_carrier.initialise_board(self._percival_params)
        cmd_msgs += self._board_settings_plugin.initialise_board(self._percival_params)
        for cmd_msg in cmd_msgs:
            try:
                resp = self._txrx.send_recv_message(cmd_msg)
            except:
                log.warning("no response (message: %s", cmd_msg)


def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--write", default="False", help="Write the initialisation configuration to the board")
#    parser.add_argument("-o", "--output", action='store', help="Output HDF5 filename")
#    parser.add_argument("-p", "--period", action='store', type=float, default=1.0, help="Control the loop period time")
#    parser.add_argument("channel", action='store', help="Control Channel to scan")
    args = parser.parse_args()
    return args

def main():
    args = options()
    log.info (args)

    with TxRxContext(board_ip_address) as trx:

        if args.write == "True":
            percival = PercivalBoard(trx)
            percival.initialise_board()

        ## Now read back and check we are matching

        percival_params = PercivalParameters()
        percival_params.load_ini()

        bs = BoardSettings(trx, const.BoardTypes.left)
        cmd_msg = bs.initialise_board(percival_params)
        bs = BoardSettings(trx, const.BoardTypes.bottom)
        cmd_msg += bs.initialise_board(percival_params)
        bs = BoardSettings(trx, const.BoardTypes.carrier)
        cmd_msg += bs.initialise_board(percival_params)
        bs = BoardSettings(trx, const.BoardTypes.plugin)
        cmd_msg += bs.initialise_board(percival_params)

        scanrange = range(0x013A, 0x0145 + 1, 1)
        expected_bytes = None
        for addr in scanrange:
            msg = encode_message(addr, 0x00000000)

            #log.debug("Qurying address: %X ...", addr)
            try:
                resp = trx.send_recv(msg, expected_bytes)
            except:
                log.warning("no response (addr: %X", addr)
                continue
            data = decode_message(resp)
            #log.info("Got from addr: 0x%04X bytes: %d  words: %d", addr, len(resp), len(data))
            for (a, w) in data:
                test_data = decode_message(cmd_msg[a].message)
                ta, tw = test_data[0]
                if w == tw:
                    log.info("Match address 0X%02X [0X%08X] == [0X%08X]", a, w, tw)
                else:
                    log.info("Mismatch!!")

if __name__ == '__main__':
    main()