'''
Created on 20 May 2016

@author: Alan Greer
'''
from __future__ import print_function
from future.utils import raise_with_traceback

import os, time
import argparse

import logging

import os
from collections import OrderedDict
from configparser import SafeConfigParser
from percival.carrier import const
from percival.carrier.channels import MonitoringChannel
from percival.carrier.devices import MAX31730, DeviceFactory
from percival.carrier.settings import BoardSettings
from percival.carrier.system import SystemCommand
from percival.carrier.txrx import TxRx, TxRxContext, hexify
from percival.carrier.values import BoardValues
from percival.configuration import ChannelParameters, BoardParameters

from percival.detector.ipc_channel import IpcChannel
from percival.detector.ipc_message import IpcMessage
from percival.detector.ipc_reactor import IpcReactor


class PercivalParameters(object):
    def __init__(self):
        self._log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
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
        self._log.info(self._channel_params.control_channels)

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

    def monitoring_channel_by_name(self, channel_name):
        logging.debug(self._channel_params)
        return self._channel_params.monitoring_channels_by_name(channel_name)

    @property
    def monitoring_channels(self):
        return self._channel_params.monitoring_channels


class PercivalBoard(object):
    def __init__(self, txrx):
        self._log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self._txrx = txrx
        self._percival_params = PercivalParameters()
        self._board_settings = {}
        self._board_values ={}
        self._temperatures = {}
        self._board_settings[const.BoardTypes.left] = BoardSettings(txrx, const.BoardTypes.left)
        self._board_settings[const.BoardTypes.bottom] = BoardSettings(txrx, const.BoardTypes.bottom)
        self._board_settings[const.BoardTypes.carrier] = BoardSettings(txrx, const.BoardTypes.carrier)
        self._board_settings[const.BoardTypes.plugin] = BoardSettings(txrx, const.BoardTypes.plugin)
        self._board_values[const.BoardTypes.carrier] = BoardValues(txrx, const.BoardTypes.carrier)
        self._sys_cmd = SystemCommand(txrx)
        self.load_ini()

    def load_ini(self):
        self._percival_params.load_ini()

    def initialise_board(self):
        cmd_msgs = self._board_settings[const.BoardTypes.left].initialise_board(self._percival_params)
        cmd_msgs += self._board_settings[const.BoardTypes.bottom].initialise_board(self._percival_params)
        cmd_msgs += self._board_settings[const.BoardTypes.carrier].initialise_board(self._percival_params)
        cmd_msgs += self._board_settings[const.BoardTypes.plugin].initialise_board(self._percival_params)
        for cmd_msg in cmd_msgs:
            try:
                resp = self._txrx.send_recv_message(cmd_msg)
            except:
                self._log.warning("no response (message: %s", cmd_msg)

    def load_channels(self):
        self._board_settings[const.BoardTypes.left].readback_monitoring_settings()
        self._board_settings[const.BoardTypes.bottom].readback_monitoring_settings()
        self._board_settings[const.BoardTypes.carrier].readback_monitoring_settings()
        self._board_settings[const.BoardTypes.plugin].readback_monitoring_settings()
        # Get the list of monitor names
        monitors = self._percival_params.monitoring_channels
        for monitor in monitors:
            # Check for the board type
            bt = const.BoardTypes(monitor.Board_type)
            if bt != const.BoardTypes.prototype:
                settings = self._board_settings[bt].device_monitoring_settings(monitor.UART_address)
                mc = MonitoringChannel(self._txrx, monitor, settings)
                if const.DeviceFamily(mc._channel_ini.Component_family_ID) == const.DeviceFamily.MAX31730:
                    self._log.info("Adding %s [%s] to monitor set", (const.DeviceFamily(mc._channel_ini.Component_family_ID)).name, mc._channel_ini.Channel_name)
                    description, device = DeviceFactory[const.DeviceFamily(mc._channel_ini.Component_family_ID)]
                    self._temperatures[mc._channel_ini.Channel_name] = device(mc)

    def set_global_monitoring(self, state=True):
        if state == True:
            self._sys_cmd.send_command(const.SystemCmd.enable_global_monitoring)
        else:
            self._sys_cmd.send_command(const.SystemCmd.disable_global_monitoring)

    def update(self, name):
        self._temperatures[name].update()

    def temperature(self, name):
        if self._temperatures.has_key(name):
            return self._temperatures[name].temperature

    def callback(self, msg):
        self._log.debug("Called Back!!")
        self._log.debug("%s", msg)

    def timer(self):
        self._log.debug("Timer called back")
        self._log.debug(self._board_values[const.BoardTypes.carrier].read_values())

    def update_status(self):
        self._log.debug("Update status called")

