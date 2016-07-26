'''
Created on 20 May 2016

@author: Alan Greer
'''
from __future__ import print_function
from future.utils import raise_with_traceback

import logging

from percival.carrier import const
from percival.carrier.channels import ControlChannel, MonitoringChannel
from percival.carrier.devices import DeviceFactory
from percival.carrier.registers import generate_register_maps, BoardValueRegisters
from percival.carrier.settings import BoardSettings
from percival.carrier.system import SystemCommand
from percival.carrier.txrx import TxRx
from percival.carrier.values import BoardValues
from percival.configuration import ChannelParameters, BoardParameters, ControlParameters


class PercivalParameters(object):
    def __init__(self):
        self._log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self._control_params = ControlParameters("config/percival.ini")
        self._board_params = {
            const.BoardTypes.left: BoardParameters("config/Board LEFT.ini"),
            const.BoardTypes.bottom: BoardParameters("config/Board BOTTOM.ini"),
            const.BoardTypes.carrier: BoardParameters("config/Board CARRIER.ini"),
            const.BoardTypes.plugin: BoardParameters("config/Board PLUGIN.ini")
        }
        self._channel_params = ChannelParameters("config/Channel parameters.ini")

    def load_ini(self):
        self._control_params.load_ini()
        self._board_params[const.BoardTypes.left].load_ini()
        self._board_params[const.BoardTypes.bottom].load_ini()
        self._board_params[const.BoardTypes.carrier].load_ini()
        self._board_params[const.BoardTypes.plugin].load_ini()
        self._channel_params.load_ini()
        self._log.info(self._channel_params.control_channels)

    @property
    def carrier_ip(self):
        return self._control_params.carrier_ip

    @property
    def status_endpoint(self):
        return self._control_params.status_endpoint

    @property
    def control_endpoint(self):
        return self._control_params.control_endpoint

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

    def monitoring_channel_name_by_index_and_board_type(self, index, type):
        return self._channel_params.monitoring_channel_name_by_id_and_board_type(index, type)

    def monitoring_channel_by_name(self, channel_name):
        self._log.debug(self._channel_params)
        return self._channel_params.monitoring_channels_by_name(channel_name)

    @property
    def monitoring_channels(self):
        return self._channel_params.monitoring_channels

    @property
    def control_channels(self):
        return self._channel_params.control_channels


class PercivalDetector(object):
    def __init__(self):
        self._log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self._txrx = None
        self._global_monitoring = False
        self._percival_params = PercivalParameters()
        self._board_settings = {}
        self._board_values ={}
        self._monitors = {}
        self._controls = {}
        self._sys_cmd = None
        self.load_ini()
        self.setup_control()

    def load_ini(self):
        self._percival_params.load_ini()

    def setup_control(self):
        self._log.critical("Carrier IP set as: %s", self._percival_params.carrier_ip)
        self._txrx = TxRx(self._percival_params.carrier_ip)
        self._board_settings[const.BoardTypes.left] = BoardSettings(self._txrx, const.BoardTypes.left)
        self._board_settings[const.BoardTypes.bottom] = BoardSettings(self._txrx, const.BoardTypes.bottom)
        self._board_settings[const.BoardTypes.carrier] = BoardSettings(self._txrx, const.BoardTypes.carrier)
        self._board_settings[const.BoardTypes.plugin] = BoardSettings(self._txrx, const.BoardTypes.plugin)
        self._board_values[const.BoardTypes.carrier] = BoardValues(self._txrx, const.BoardTypes.carrier)
        self._sys_cmd = SystemCommand(self._txrx)

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
        # Readback the monitoring settings
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
                self._log.critical("Adding %s [%s] to monitor set", (const.DeviceFamily(mc._channel_ini.Component_family_ID)).name, mc._channel_ini.Channel_name)
                description, device = DeviceFactory[const.DeviceFamily(mc._channel_ini.Component_family_ID)]
                self._monitors[mc._channel_ini.Channel_name] = device(mc._channel_ini.Channel_name, mc)

        # Readback the control settings
        self._board_settings[const.BoardTypes.left].readback_control_settings()
        self._board_settings[const.BoardTypes.bottom].readback_control_settings()
        self._board_settings[const.BoardTypes.carrier].readback_control_settings()
        self._board_settings[const.BoardTypes.plugin].readback_control_settings()
        # Get the list of control names
        controls = self._percival_params.control_channels
        for control in controls:
            # Check for the board type
            bt = const.BoardTypes(control.Board_type)
            if bt != const.BoardTypes.prototype:
                settings = self._board_settings[bt].device_control_settings(control.UART_address)
                cc = ControlChannel(self._txrx, control, settings)
                self._log.critical("Adding %s [%s] to control set", (const.DeviceFamily(cc._channel_ini.Component_family_ID)).name, cc._channel_ini.Channel_name)
                description, device = DeviceFactory[const.DeviceFamily(cc._channel_ini.Component_family_ID)]
                self._controls[cc._channel_ini.Channel_name] = device(cc._channel_ini.Channel_name, cc)

    def set_global_monitoring(self, state=True):
        if state:
            self._sys_cmd.send_command(const.SystemCmd.enable_global_monitoring)
            self._sys_cmd.send_command(const.SystemCmd.enable_device_level_safety_controls)
            self._global_monitoring = True
        else:
            self._global_monitoring = False
            self._sys_cmd.send_command(const.SystemCmd.disable_global_monitoring)
            self._sys_cmd.send_command(const.SystemCmd.disable_device_level_safety_controls)

    def system_command(self, cmd):
        self._sys_cmd.send_command(const.SystemCmd[cmd])

    def set_value(self, device, value, timeout=0.1):
        if device in self._controls:
            self._controls[device].set_value(value, timeout)

    def update(self, name):
        self._temperatures[name].update()

    def temperature(self, name):
        if self._temperatures.has_key(name):
            return self._temperatures[name].temperature

    def read(self, parameter):
        self._log.critical("Reading data %s", parameter)

        # First check to see if parameter is a keyword
        if parameter == "controls":
            reply = {}
            for control in self._controls:
                reply[control] = self._controls[control].device

        elif parameter == "monitors":
            reply = {}
            for monitor in self._monitors:
                reply[monitor] = self._monitors[monitor].device

        elif parameter == "device":
            reply = {
                const.BoardTypes.carrier.name: {
                    "name":           self._percival_params.board_name(const.BoardTypes.carrier),
                    "type":           self._percival_params.board_type(const.BoardTypes.carrier).name,
                    "controls_count": self._percival_params.control_channels_count(const.BoardTypes.carrier),
                    "monitors_count": self._percival_params.monitoring_channels_count(const.BoardTypes.carrier)
                },
                const.BoardTypes.left.name: {
                    "name": self._percival_params.board_name(const.BoardTypes.left),
                    "type": self._percival_params.board_type(const.BoardTypes.left).name,
                    "controls_count": self._percival_params.control_channels_count(const.BoardTypes.left),
                    "monitors_count": self._percival_params.monitoring_channels_count(const.BoardTypes.left)
                },
                const.BoardTypes.bottom.name: {
                    "name": self._percival_params.board_name(const.BoardTypes.bottom),
                    "type": self._percival_params.board_type(const.BoardTypes.bottom).name,
                    "controls_count": self._percival_params.control_channels_count(const.BoardTypes.bottom),
                    "monitors_count": self._percival_params.monitoring_channels_count(const.BoardTypes.bottom)
                },
                const.BoardTypes.plugin.name: {
                    "name": self._percival_params.board_name(const.BoardTypes.plugin),
                    "type": self._percival_params.board_type(const.BoardTypes.plugin).name,
                    "controls_count": self._percival_params.control_channels_count(const.BoardTypes.plugin),
                    "monitors_count": self._percival_params.monitoring_channels_count(const.BoardTypes.plugin)
                },
            }

        elif parameter == "status":
            reply = {}
            for monitor in self._monitors:
                self._log.critical("Monitor: %s", monitor)
                reply[monitor] = self._monitors[monitor].status

        # Check to see if the parameter is a monitoring device that we own
        elif parameter in self._monitors:
            reply = { parameter: self._monitors[parameter].status }

        else:
            reply = { "error": "Parameter not found" }

        return reply

    def update_status(self):
        self._log.info("Update status callback called")
        status_msg = {}
        if self._global_monitoring:
            response = self._board_values[const.BoardTypes.carrier].read_values()
            self._log.debug(response)
            read_maps = generate_register_maps(response)
            self._log.debug(read_maps)

            readback_block = BoardValueRegisters[const.BoardTypes.carrier]
            for addr, value in response:
                offset = addr - readback_block.start_address
                name = self._percival_params.monitoring_channel_name_by_index_and_board_type(offset, const.BoardTypes.carrier)
                if self._monitors.has_key(name):
                    self._monitors[name].update(read_maps[offset])
                    status_msg[name] = self._monitors[name].status

            self._log.debug("Status: %s", status_msg)
        return status_msg
