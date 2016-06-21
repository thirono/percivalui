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


class PercivalBoard(object):
    def __init__(self, txrx):
        self._log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self._txrx = txrx
        self._global_monitoring = False
        self._ctrl_channel = None
        self._status_channel = None
        self._reactor = IpcReactor()
        self._percival_params = PercivalParameters()
        self._board_settings = {}
        self._board_values ={}
        self._monitors = {}
        self._controls = {}
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

    def setup_control_channel(self, endpoint):
        self._ctrl_channel = IpcChannel(IpcChannel.CHANNEL_TYPE_PAIR)
        self._ctrl_channel.bind(endpoint)
        self._reactor.register_channel(self._ctrl_channel, self.configure)

    def setup_status_channel(self, endpoint):
        self._status_channel = IpcChannel(IpcChannel.CHANNEL_TYPE_PUB)
        self._status_channel.bind(endpoint)

    def start_reactor(self):
        self._reactor.register_timer(1000, 0, self.update_status)
        self._reactor.run()

    def set_global_monitoring(self, state=True):
        if state:
            self._sys_cmd.send_command(const.SystemCmd.enable_global_monitoring)
            self._sys_cmd.send_command(const.SystemCmd.enable_device_level_safety_controls)
            self._global_monitoring = True
        else:
            self._global_monitoring = False
            self._sys_cmd.send_command(const.SystemCmd.disable_global_monitoring)
            self._sys_cmd.send_command(const.SystemCmd.disable_device_level_safety_controls)

    def update(self, name):
        self._temperatures[name].update()

    def temperature(self, name):
        if self._temperatures.has_key(name):
            return self._temperatures[name].temperature

    def configure(self, msg):
        self._log.critical("Received message on configuration channel: %s", msg)
        if msg.get_msg_type() == IpcMessage.MSG_TYPE_CMD and msg.get_msg_val() == IpcMessage.MSG_VAL_CMD_CONFIGURE:
            if msg.has_param("status_loop"):
                if msg.get_param("status_loop") == "run":
                    self.set_global_monitoring(True)
                if msg.get_param("status_loop") == "stop":
                    self.set_global_monitoring(False)

            if msg.has_param("list"):
                # What are we listing
                list = msg.get_param("list")
                self._log.critical("Requested list of %s", list)
                if list == "controls":
                    reply = {}
                    for control in self._controls:
                        reply[control] = self._controls[control].device
                    # Reply with the list of control devices
                    reply_msg = IpcMessage(IpcMessage.MSG_TYPE_ACK, IpcMessage.MSG_VAL_CMD_CONFIGURE)
                    reply_msg.set_param("controls", reply)
                    self._log.critical("Reply with list of controls: %s", reply_msg.encode())
                    self._ctrl_channel.send(reply_msg.encode())

                if list == "monitors":
                    reply = {}
                    for monitor in self._monitors:
                        reply[monitor] = self._monitors[monitor].device
                    # Reply with the list of monitor devices
                    reply_msg = IpcMessage(IpcMessage.MSG_TYPE_ACK, IpcMessage.MSG_VAL_CMD_CONFIGURE)
                    reply_msg.set_param("monitors", reply)
                    self._log.critical("Reply with list of monitors: %s", reply_msg.encode())
                    self._ctrl_channel.send(reply_msg.encode())

    def timer(self):
        self._log.debug("Timer called back")
        self._log.debug(self._board_values[const.BoardTypes.carrier].read_values())

    def update_status(self):
        self._log.info("Update status callback called")
        if self._global_monitoring:
            response = self._board_values[const.BoardTypes.carrier].read_values()
            self._log.debug(response)
            read_maps = generate_register_maps(response)
            self._log.debug(read_maps)

            readback_block = BoardValueRegisters[const.BoardTypes.carrier]
            status_msg = IpcMessage(IpcMessage.MSG_TYPE_NOTIFY, IpcMessage.MSG_VAL_CMD_STATUS)
            for addr, value in response:
                offset = addr - readback_block.start_address
                name = self._percival_params.monitoring_channel_name_by_index_and_board_type(offset, const.BoardTypes.carrier)
                if self._monitors.has_key(name):
                    self._monitors[name].update(read_maps[offset])
                    status_msg.set_param(name, self._monitors[name].status)

            self._log.debug("Publishing: %s", status_msg.encode())
            self._status_channel.send(status_msg.encode())



