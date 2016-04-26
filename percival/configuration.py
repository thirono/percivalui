'''
Configuration of the Percival Detector system can be loaded from various files.

This module contain classes and functions to manage the loading of configurations.
'''
from __future__ import unicode_literals, absolute_import
from future.utils import raise_with_traceback

import logging

import os
import re
from collections import OrderedDict
from configparser import SafeConfigParser


logger = logging.getLogger(__name__)

env_config_dir = "PERCIVAL_CONFIG_DIR"
'''
The environment variable PERCIVAL_CONFIG_DIR can optionally contain a path where
to look for configuration files at runtime. The current working directory and direct/full
paths will always override this directory, which will only be searched if the file
cannot be found
'''

positive_configuration = ["true", "yes", "on", "enable", "enabled"]
negative_configuration = ["false", "no", "off", "disable", "disabled"]


def find_file(filename, env=None):
    '''Search for a file and return the full path if it can be found.
    
    Raises IOError if a file of the given name cannot be found.
    
    :param filename: The filename to search for. Can be relative or full path.
    :param env: The name of an environment variable which can contain a list of
                colon-separated directories. These directories (if any) will be
                searched for the :param:`filename` if it cannot be found.
    :returns: An absolute path to the file of the same name.
    '''
    # Check if the filename exist as a relative or absolute path
    if os.path.isfile(filename):
        return os.path.abspath(filename)

    # Check  if the file exist in one of the search paths, indicated by
    # the user in an environemnt variable
    search_paths = os.getenv(env_config_dir, "")
    if search_paths:
        for path in search_paths.split(":"):
            fn = os.path.abspath( os.path.join([path, filename]) )
            if os.path.isfile(fn):
                return fn

    # All other searches failed. We cant find this file. Raise exception.
    raise IOError


class IniSectionParameters(object):
    """Mixin to be used by classes that load configuration sections from INI files.

    Child classes must implement a self._parameters dictionary of tuples: {<name>: (<value>, <datatype>)}
    """
    def __getattr__(self, name):
        if name in self._parameters.keys():
            return self._parameters[name][0]
        else:
            raise_with_traceback(AttributeError("No parameter: %s"%name))

    def __setattr__(self, name, value):
        if name not in self._parameters.keys():
            return object.__setattr__(self, name, value)
        else:
            if self._parameters[name][1] == type(value):
                self._parameters[name] = (value, type(value))
            else:
                raise_with_traceback(TypeError("Invalid type %s for parameter \"%s\""%(type(value), name)))

    def parameters(self):
        """return a list of parameter names"""
        return self._parameters.keys()

    def get_type(self, parameter):
        return self._parameters[parameter][1]

    def __str__(self):
        param_str = ""
        for (name, value) in self._parameters.items():
            param_str += "%s=%s, "%(name, value[0])
        s = "<%s: Parameters = %s>"%(self.__class__.__name__, param_str)
        return s

    def __repr__(self):
        return self.__str__()


class ControlChannelIniParameters(IniSectionParameters):
    section_regexp = re.compile(r'^Control_channel<\d{4}>$')

    def __init__(self, channel_number):
        object.__setattr__(self, '_parameters', {})  # This prevents infinite recursion when setting attributes
        self._channel_number = channel_number
        self._parameters = {"UART_address": (0, int),
                            "Board_type": (0, int),
                            "Channel_name": (0, str),
                            "I2C_address": (0, int),
                            "I2C_Sub_address": (0, int),
                            "I2C_bus_selection": (0, int),
                            "Component_family_ID": (0, int),
                            "Device_ID": (0, int),
                            "Channel_ID": (0, int),
                            "Minimum_value": (0, int),
                            "Maximum_value": (0, int),
                            "Default_OFF_value": (0, int),
                            "Default_ON_value": (0, int),
                            "Value": (0, int),
                            "Power_status": (0, bool),
                            "Channel_offset": (0, int),
                            "Channel_multiplier": (0, int),
                            "Channel_divider": (0, int),
                            "Channel_unit": (0, str),
                            }


class MonitoringChannelIniParameters(IniSectionParameters):
    section_regexp = re.compile(r'^Monitoring_channel<\d{4}>$')

    def __init__(self, channel_number):
        object.__setattr__(self, '_parameters', {})  # This prevents infinite recursion when setting attributes
        self._channel_number = channel_number
        self._parameters = {"UART_address": (0, int),
                            "Board_type": (0, int),
                            "Channel_name": (0, str),
                            "I2C_address": (0, int),
                            "I2C_Sub_address": (0, int),
                            "I2C_bus_selection": (0, int),
                            "Component_family_ID": (0, int),
                            "Device_ID": (0, int),
                            "Channel_ID": (0, int),
                            "Extreme_low_threshold": (0, int),
                            "Extreme_high_threshold": (0, int),
                            "Low_threshold": (0, int),
                            "High_threshold": (0, int),
                            "Monitoring": (0, int),
                            "Read_frequency": (0, int),
                            "Safety_exception_threshold": (0, int),
                            "Minimum_value": (0, int),
                            "Maximum_value": (0, int),
                            "Offset": (0, int),
                            "Multiplier": (0, int),
                            "Divider": (0, int),
                            "Unit": (0, str),
                            }


class ChannelParameters(object):
    def __init__(self, ini_file):
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self._ini_filename = find_file(ini_file)
        self.conf = None

        self._control_channels = None
        self._monitoring_channels = None

    def load_ini(self):
        self._control_channels = None
        self._monitoring_channels = None
        self.conf = SafeConfigParser(dict_type=OrderedDict)
        self.conf.read(self._ini_filename)

    @staticmethod
    def _get_channel_number(section_name):
        match = re.match(r'^.*_channel<(\d{4})>$', section_name)
        if match:
            result = int(match.group(1))
            return result
        else:
            raise_with_traceback(RuntimeError("Unable to detect channel name from \"%s\""%section_name))

    def _get_channel_matching(self, regexp):
        sections_matching = []
        for section in self.conf.sections():
            if regexp.match(section):
                sections_matching.append(section)
        return sections_matching

    def control_channels_by_name(self, name):
        return self._get_channels_by_name(self.control_channels, name)

    def monitoring_channels_by_name(self, name):
        return self._get_channels_by_name(self.monitoring_channels, name)

    @property
    def control_channels(self):
        if self._control_channels:
            return self._control_channels
        self._control_channels = self._get_channels(ControlChannelIniParameters)
        return self._control_channels

    @property
    def monitoring_channels(self):
        if self._monitoring_channels:
            return self._monitoring_channels
        self._monitoring_channels = self._get_channels(MonitoringChannelIniParameters)
        return self._monitoring_channels

    def _get_channels(self, channel_class):
        channels = []
        sections = self._get_channel_matching(channel_class.section_regexp)
        for section in sections:
            channel_number = self._get_channel_number(section)
            channel = channel_class(channel_number)
            for param in channel.parameters():
                parameter_type = channel.get_type(param)
                if parameter_type == int:
                    value = self.conf.getint(section, param)
                elif parameter_type == str:
                    value = self.conf.get(section, param)
                    value = str(value.strip("\""))  # Get rid of any double quotes from the ini file
                elif parameter_type == bool:
                    str_value = self.conf.get(section, param)
                    if str_value.lower() in positive_configuration:
                        value = True
                    elif str_value.lower() in negative_configuration:
                        value = False
                    else:
                        raise_with_traceback(TypeError("Unsupported boolean: %s = \"%s\""%(param, str_value)))
                else:
                    raise_with_traceback(TypeError("Unsupported parameter type %s"%str(parameter_type)))
                channel.__setattr__(param, value)
            self.log.debug("Appending channel: %s", channel)
            channels.append(channel)
        return channels

    @staticmethod
    def _get_channels_by_name(channel_list, name):
        result = []
        for ch in channel_list:
            if ch.Channel_name == name:
                result.append(ch)
        if len(result) == 1:
            result = result[0]
        return result

    def __str__(self):
        channels = "Control channels: "
        if self._control_channels:
            channels += str(len(self._control_channels))
        else:
            channels += "[]"
        channels += " Monitoring channels: "
        if self._monitoring_channels:
            channels += str(len(self._monitoring_channels))
        else:
            channels += "[]"
        s = "<%s: inifile: %s %s>"%(self.__class__.__name__, self._ini_filename, channels)
        return s

    def __repr__(self):
        return self.__str__()


