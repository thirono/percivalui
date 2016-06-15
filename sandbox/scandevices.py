'''
Created on 19 May 2015

@author: Ulrik Pedersen
'''
from __future__ import print_function

import os, time
import argparse
import numpy as np
import h5py
from collections import OrderedDict

import logging
from percival.log import log

from percival.carrier import const
from percival.carrier.registers import UARTRegister, BoardRegisters, generate_register_maps
from percival.carrier.devices import DeviceFunction, DeviceCmd, DeviceFamilyFeatures, DeviceFamily
from percival.carrier.settings import BoardSettings
from percival.carrier.txrx import TxRx, TxRxContext, hexify
from percival.carrier.channels import ControlChannel
from percival.configuration import ChannelParameters, ControlChannelIniParameters

board_ip_address = os.getenv("PERCIVAL_CARRIER_IP")


class ReadMonitors(object):
    def __init__(self, txrx, uart_block, ini_params, board_type):
        """

        :param txrx:
        :param uart_block:
        :type: :obj:`percival.carrier.const.UARTBlock`
        """
        self._txrx = txrx
        self._uart_block = uart_block
        self._board_type = board_type
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
            name = ini_params.monitoring_channel_name_by_id_and_board_type(index, self._board_type)
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

    @property
    def channel_data(self):
        """
        Get all the recorded channel data as a (channel) dict of (field) dicts with numpy arrays:

            { "channel one": { "field_one": numpy.array([...])},
                               "field_two": numpy.array([...])},
              "channel two": { "field_one": numpy.array([...])},
                               "field_two": numpy.array([...])}}

        :return: dictionary of dictionaries of numpy arrays
        """
        result = {}
        for channel_name, channel_data in self._channel_data.items():
            fields = channel_data[0].map_fields
            channel = {}
            for read_value_field in fields:
                num_bits = channel_data[0][read_value_field].num_bits
                dtype = np.uint8
                if num_bits > 8: dtype = np.uint16
                data = np.array([readvalue[read_value_field].value for readvalue in channel_data], dtype=dtype)
                channel.update({read_value_field: data})
            result.update({channel_name: channel})
        return result


def store_monitor_data(args, data_dict):
    """
    Store recorded ReadMonitor data to a HDF5 file.

    :param args: command line arguments supplied to the file.
    :param data_dict: dictionary of `ReadData` objects.
    :return:
    """
    filename = args.output
    with h5py.File(filename, 'w') as f:
        f.attrs["range"] = bytes(args.range)
        f.attrs["channel"] = bytes(args.channel)
        for channel_name, channel_fields in data_dict.items():
            log.debug("=========== Creating group %s ============", channel_name)
            group = f.create_group(channel_name)
            for field_name, data_array in channel_fields.items():
                log.debug("--- Writing %s data: %s ", field_name, data_array)
                group.create_dataset(field_name, data=data_array)


def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--range", default="0,100,20", help="Scan range in integers formatted like this: start,stop,step")
    parser.add_argument("-o", "--output", action='store', help="Output HDF5 filename")
    parser.add_argument("-p", "--period", action='store', type=float, default=1.0, help="Control the loop period time")
    parser.add_argument("channel", action='store', help="Control Channel to scan")
    args = parser.parse_args()

    args.range = [int(x) for x in args.range.split(',')]
    return args


def main():
    args = options()
    log.info (args)

    with TxRxContext(board_ip_address) as trx:
        ini_params = ChannelParameters("config/Channel parameters.ini")
        ini_params.load_ini()

        # Get the Control Channels
        log.debug("Control Channels: %s", str(ini_params.control_channels))
        log.debug("Monitoring Channels: %s", str(ini_params.monitoring_channels))
        log.debug("INI parameters: %s", ini_params)

        bs = BoardSettings(trx, const.BoardTypes.carrier)
        bs.readback_control_settings()

        ini = ini_params.control_channels_by_name(args.channel)
        log.info("ini: %s", ini)

        cc_settings = bs.device_control_settings(ini.UART_address)
        log.info("Control Channel #2 settings from board: %s", hexify(cc_settings))

        log.debug("Creating control channel")
        cc = ControlChannel(trx, ini, cc_settings)

        readmon = ReadMonitors(trx, const.READ_VALUES_CARRIER, ini_params, const.BoardTypes.carrier)

        tstamp = time.time()
        for new_value in range(*args.range):
            log.info("Writing DAC channel 2 value = %d", new_value)
            echo_result = cc.set_value(new_value, timeout=1.0)
            log.info("ECHO: %s", echo_result)
            if echo_result.read_value != new_value:
                log.warning("  Echo result does not match demanded value (%d != %d)", echo_result.read_value, new_value)
            dt = time.time() - tstamp
            if args.period - dt > 0.0:
                time.sleep(args.period - dt)
                log.debug("sleeping: %f sec", args.period - dt)
            tstamp = time.time()
            adcs = readmon.read_carrier_monitors()
            log.info("Read carrier monitoring channels: %s", adcs.keys())

        # check if we need to execute one more iteration
        if (args.range[2] > 0 and new_value < args.range[1]) or (args.range[2] < 0 and new_value > args.range[1]):
            new_value = args.range[1]
            # Execute one last time to include the maximum value
            log.info("Writing DAC channel 2 value = %d", new_value)
            echo_result = cc.set_value(new_value, timeout=1.0)
            log.info("ECHO: %s", echo_result)
            if echo_result.read_value != new_value:
                log.warning("  Echo result does not match demanded value (%d != %d)", echo_result.read_value, new_value)
            dt = time.time() - tstamp
            if args.period - dt > 0.0:
                time.sleep(args.period - dt)
                log.debug("sleeping: %f sec", args.period - dt)
            tstamp = time.time()
            adcs = readmon.read_carrier_monitors()
            log.info("Read carrier monitoring channels: %s", adcs.keys())


        log.info(readmon.channel_data)
    if args.output:
        store_monitor_data(args, readmon.channel_data)


if __name__ == '__main__':
    main()