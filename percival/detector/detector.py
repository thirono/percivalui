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
    """
    High level representation of Parameters loaded from ini files.

    Currently the files are all hardcoded here which is not very elegant.

    A better approach would be to be able to specify the files within the main ini file, and for the files to be
    searched in standard locations or through environment variables.  This is partially implemented for the
    ChannelParameters class.

    ini files are parsed for overall control parameters, for each of the boards and finally for the channels.

    All ini settings are stored and can be accessed through this class.
    """
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
        """
        Load the initialisation files for the control, four board types and for the channels
        """
        self._control_params.load_ini()
        self._board_params[const.BoardTypes.left].load_ini()
        self._board_params[const.BoardTypes.bottom].load_ini()
        self._board_params[const.BoardTypes.carrier].load_ini()
        self._board_params[const.BoardTypes.plugin].load_ini()
        self._channel_params.load_ini()
        self._log.info(self._channel_params.control_channels)

    @property
    def carrier_ip(self):
        """
        Return the IP address of the carrier board

        :returns: IP address of the carrier board
        :rtype: str
        """
        return self._control_params.carrier_ip

    def board_name(self, type):
        """
        Return the name of the specified board type

        :param type: Which board to return the name
        :type type: const.BoardTypes
        :returns: Name of the specified board
        :rtype: str
        """
        return self._board_params[type].board_name

    def board_type(self, type):
        """
        Return the type of the specified board

        :param type: Which board to return the type
        :type type: const.BoardTypes
        :returns: Type of the specified board
        :rtype: str
        """
        return self._board_params[type].board_type

    def control_channels_count(self, type):
        """
        Return the number of control channels of the specified board

        :param type: Which board to return the number of control channels
        :type type: const.BoardTypes
        :returns: Number of control channels
        :rtype: int
        """
        return self._board_params[type].control_channels_count

    def monitoring_channels_count(self, type):
        """
        Return the number of monitor channels of the specified board

        :param type: Which board to return the number of monitor channels
        :type type: const.BoardTypes
        :returns: Number of monitor channels
        :rtype: int
        """
        return self._board_params[type].monitoring_channels_count

    def control_channel_by_address(self, uart_address):
        """
        Search for the control channel by its UART address

        :param uart_address: Address of the control channel
        :type uart_address: int
        :returns: Control channel ini parameters
        :rtype: configuration.ControlChannelIniParameters
        """
        return self._channel_params.control_channel_by_address(uart_address)

    def monitoring_channel_by_address(self, uart_address):
        """
        Search for the monitor channel by its UART address

        :param uart_address: Address of the monitor channel
        :type uart_address: int
        :returns: Monitor channel ini parameters
        :rtype: configuration.MonitorChannelIniParameters
        """
        return self._channel_params.monitoring_channel_by_address(uart_address)

    def monitoring_channel_name_by_index_and_board_type(self, index, type):
        """
        Search for the monitor channel name by its ini file index and the board type

        :param index: Index of the channel
        :type index: int
        :param index: Which board to search
        :type index: const.BoardTypes
        :returns: Monitor channel name
        :rtype: str
        """
        return self._channel_params.monitoring_channel_name_by_id_and_board_type(index, type)

    def monitoring_channel_by_name(self, channel_name):
        """
        Search for the monitor channel by its name

        :param channel_name: Name of the monitor channel
        :type channel_name: str
        :returns: Monitor channel ini parameters
        :rtype: configuration.MonitorChannelIniParameters
        """
        self._log.debug(self._channel_params)
        return self._channel_params.monitoring_channels_by_name(channel_name)

    @property
    def monitoring_channels(self):
        """
        Return a list of `MonitoringChannelIniParameters`

        :returns: List of monitor channel ini parameters
        :rtype: list
        """
        return self._channel_params.monitoring_channels

    @property
    def control_channels(self):
        """
        Return a list of `ControlChannelIniParameters`

        :returns: List of control channel ini parameters
        :rtype: list
        """
        return self._channel_params.control_channels


class PercivalDetector(object):
    """
    High level representation of Detector hardware.
    This class manages the connection to the hardware, as well as the configuration and specific setup.

    Low level hardware complexity is handled internally and a simple interface is presented as a public API
    for control and status monitoring.

    This class has no threading internally but should be considered thread safe (needs checking)
    """
    def __init__(self, initialise_hardware=True):
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
        if initialise_hardware:
            self.initialise_board()
        self.load_channels()

    def load_ini(self):
        """
        Load the initialisation files for the detector
        """
        self._percival_params.load_ini()

    def setup_control(self):
        """
        Setup the control interface for the detector.
        This currently:
        Creates the TxRx connection class and connects to the hardware
        Creates the BoardSettings classes to describe the hardware.  These can be used to either download hardware
        configurations from ini files or to read settings from the hardware.
        Creates a SystemCommand instance which can be used to send system commands to the hardware.
        """
        self._log.critical("Carrier IP set as: %s", self._percival_params.carrier_ip)
        self._txrx = TxRx(self._percival_params.carrier_ip)
        self._board_settings[const.BoardTypes.left] = BoardSettings(self._txrx, const.BoardTypes.left)
        self._board_settings[const.BoardTypes.bottom] = BoardSettings(self._txrx, const.BoardTypes.bottom)
        self._board_settings[const.BoardTypes.carrier] = BoardSettings(self._txrx, const.BoardTypes.carrier)
        self._board_settings[const.BoardTypes.plugin] = BoardSettings(self._txrx, const.BoardTypes.plugin)
        self._board_values[const.BoardTypes.carrier] = BoardValues(self._txrx, const.BoardTypes.carrier)
        self._sys_cmd = SystemCommand(self._txrx)

    def initialise_board(self):
        """
        Download the configuration from ini files to the hardware.
        """
        self._log.critical("Initialise board")
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
        """
        Readout the settings from the hardware and create all control and monitoring devices according to the current
        settings coupled with the ini file descriptions.
        Monitor type devices are stored in the _monitors dictionary.
        Control type devices are stored in the _controls dictionary.
        """
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
        """
        Turn on or off global monitoring.  This sends two system commands; enable_global_monitoring and
        enable_device_level_safety_controls.
        It also sets the internal monitoring flag to either True or False.

        :param state: Turn global monitoring on (True) or off (False)
        :type state: bool
        """
        if state:
            self._sys_cmd.send_command(const.SystemCmd.enable_global_monitoring)
            self._sys_cmd.send_command(const.SystemCmd.enable_device_level_safety_controls)
            self._global_monitoring = True
        else:
            self._global_monitoring = False
            self._sys_cmd.send_command(const.SystemCmd.disable_global_monitoring)
            self._sys_cmd.send_command(const.SystemCmd.disable_device_level_safety_controls)

    def system_command(self, cmd):
        """
        Send a system command.

        :param cmd: System command to send
        :type cmd: str
        """
        self._sys_cmd.send_command(const.SystemCmd[cmd])

    def set_value(self, device, value, timeout=0.1):
        """
        Set the value of a control device.

        :param device: Name of device to set the value of
        :type device: str
        :param value: Value to set
        :type value: int
        :param timeout: Timeout for the set operation
        :type timeout: double
        """
        if device in self._controls:
            self._controls[device].set_value(value, timeout)

    def read(self, parameter):
        """
        Read a parameter from the detector.
        The parameters currently include:
        - list of control devices
        - list of monitor devices
        - hardware description
        - status of all monitors
        - status of a specific monitor

        :param parameter: Name of parameter to read status of
        :type parameter: str
        :returns: Status report of the requested parameter
        :rtype: dict
        """
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
        """
        Update the status of the monitor devices.
        The values shortcut is read out from the hardware and the status of all
        monitors is updated appropriately.
        """
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
