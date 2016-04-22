'''
Created on 8 May 2015

@author: Ulrik Pedersen
'''
from __future__ import unicode_literals, absolute_import
from future.utils import with_metaclass, raise_with_traceback
from builtins import range
import abc
from enum import Enum, unique

from percival.detector.interface import IABCMeta

import logging
logger = logging.getLogger(__name__)

@unique
class DeviceCmd(Enum):
    """Equivalent enumeration as per the documented "Supported DEVICE_CMDs"
    
    Enumerated commands include:
    
    * `no_operation`
    * `reset`
    * `initialize`
    * `set_value`
    * `get_value`
    * `set_and_get_value`
    * `set_value_on`
    * `set_value_off`
    * `enable_standby_mode`
    * `disable_standby_mode`
    * `set_word_value`
    * `get_word_value`
    * `set_page_value`
    * `get_page_value`
    """
    no_operation = 0
    reset = 1
    initialize = 2
    set_value = 3
    get_value = 4
    set_and_get_value = 5
    set_value_on = 6
    set_value_off = 7
    enable_standby_mode = 8
    disable_standby_mode = 9
    set_word_value = 10
    get_word_value = 11
    set_page_value = 12
    get_page_value = 13
    
@unique
class DeviceFunction(Enum):
    """Equivalent enumeration as per the documented "Supported DEVICE_TYPEs"
    
    Enumerated functionalities include:
    
    * `control`
    * `monitoring`
    * `eeprom`
    * `none`
    """
    control = 0
    monitoring = 1
    eeprom = 2
    none = 3
    

class DeviceFeatures(object):
    """Mapping PCB devices to their supported functionality
    
    This represent the documented table "Supported DEVICE_CMD vs device family"
    """
    def __init__(self, device_family_id, function, description ="", commands = []):
        """
            :param device_family_id: The integer device ID as documented
            :type  device_family_id: `int`
            :param function:  The enumerated functionality of the device
            :type  function:  `DeviceFunction` item
            :param description: Human readable description of the device
            :type  description: string
            :param commands: Supported commands for this device
            :type  commands: list of `DeviceCmd` items
        """
        self._device_family_id = device_family_id
        self._function = function
        self._description = description
        self._commands = commands
        
    @property
    def device_family_id(self):
        return self._device_family_id
    @property
    def function(self):
        return self._function
    @property
    def description(self):
        return self._description
    
    def supports_cmd(self, cmd):
        """Check if a given command is supported for this device
        
            :param cmd: The command to check for
            :type cmd:  `DeviceCmd`
            :returns: True if the command is supported, False if not.
            :rtype: boolean
        """
        return cmd in self._commands
        
@unique
class DeviceFamily(Enum):
    """Enumeration of the available electronic component families"""
    AD5242 = DeviceFeatures(    0, DeviceFunction.control ,     "Digital potentiometer",        [DeviceCmd.no_operation,
                                                                                                 DeviceCmd.reset,
                                                                                                 DeviceCmd.set_value,
                                                                                                 DeviceCmd.get_value,
                                                                                                 DeviceCmd.set_and_get_value,
                                                                                                 DeviceCmd.set_value_on,
                                                                                                 DeviceCmd.set_value_off] )
    """Digital potentiometer for control"""
    AD5263 = DeviceFeatures(    1, DeviceFunction.control ,     "Digital potentiometer",        [DeviceCmd.no_operation,
                                                                                                 DeviceCmd.reset,
                                                                                                 DeviceCmd.set_value,
                                                                                                 DeviceCmd.get_value,
                                                                                                 DeviceCmd.set_and_get_value] )
    """Digital potentiometer for control"""
    AD5629 = DeviceFeatures(    2, DeviceFunction.control ,     "DAC for control",              [DeviceCmd.no_operation,
                                                                                                 DeviceCmd.reset,
                                                                                                 DeviceCmd.initialize,
                                                                                                 DeviceCmd.set_value,
                                                                                                 DeviceCmd.get_value,
                                                                                                 DeviceCmd.set_and_get_value,
                                                                                                 DeviceCmd.enable_standby_mode,
                                                                                                 DeviceCmd.disable_standby_mode] )
    """DAC for control"""
    AD5669 = DeviceFeatures(    3, DeviceFunction.control ,     "DAC for control",              [DeviceCmd.no_operation,
                                                                                                 DeviceCmd.reset,
                                                                                                 DeviceCmd.initialize,
                                                                                                 DeviceCmd.set_value,
                                                                                                 DeviceCmd.get_value,
                                                                                                 DeviceCmd.set_and_get_value,
                                                                                                 DeviceCmd.enable_standby_mode,
                                                                                                 DeviceCmd.disable_standby_mode] )
    """DAC for control"""
    LTC2309 = DeviceFeatures(   7, DeviceFunction.monitoring ,  "ADC for monitoring",           [DeviceCmd.no_operation,
                                                                                                 DeviceCmd.set_value,
                                                                                                 DeviceCmd.get_value,
                                                                                                 DeviceCmd.set_and_get_value])
    """ADC for monitoring"""
    LTC2497 = DeviceFeatures(   4, DeviceFunction.monitoring ,  "ADC for monitoring",           [DeviceCmd.no_operation,
                                                                                                 DeviceCmd.set_value,
                                                                                                 DeviceCmd.get_value,
                                                                                                 DeviceCmd.set_and_get_value])
    """ADC for monitoring"""
    MAX31730 = DeviceFeatures(  5, DeviceFunction.monitoring ,  "Temperature for monitoring",   [DeviceCmd.no_operation,
                                                                                                 DeviceCmd.reset,
                                                                                                 DeviceCmd.initialize,
                                                                                                 DeviceCmd.set_and_get_value])
    """Temperature for monitoring"""
    AT24CM01 = DeviceFeatures(  6, DeviceFunction.eeprom ,      "EEPROM for on-board storage",  [DeviceCmd.no_operation,
                                                                                                 DeviceCmd.set_word_value,
                                                                                                 DeviceCmd.get_word_value,
                                                                                                 DeviceCmd.set_page_value,
                                                                                                 DeviceCmd.get_page_value])
    """EEPROM for on-board configuration storage"""


class DeviceSettings(object):
    """Mixin to be used by classes that implement the IDeviceSettings interface"""
    def __getattr__(self, name):
        if name in self._mem_map.keys():
            return self._mem_map[name].value
        else:
            raise_with_traceback(AttributeError("No attribute: %s"%name))
    
    def __setattr__(self, name, value):
        logger.debug(str(self._mem_map))
        if not name in self._mem_map.keys():
            return object.__setattr__(self, name, value)
        else:
            self._mem_map[name].value = value
            
    def parse_map(self, words):
        map_fields = [f for (k,f) in sorted(self._mem_map.items(), 
                                        key=lambda key_field: key_field[1].word_index, reverse=True)] 
        for map_field in map_fields:
            map_field.extract_field_value(words)

    def parse_map_from_tuples(self, tuples):
        words = [value for addr, value in tuples]
        self.parse_map(words)

    def generate_map(self):
        words = list(range(self.num_words))
        logger.debug("map: %s", str(self._mem_map))
        for (key,field) in self._mem_map.items():
            logger.debug("field: %s", str(field))
            field.insert_field_value(words)
            logger.debug("generate_map: words: %s", str(words))
        return words

    def __str__(self):
        map_str = ""
        map_fields = [f for (k,f) in sorted(self._mem_map.items(),
                                        key=lambda key_field: key_field[1].word_index, reverse=True)]
        for map_field in map_fields:
            map_str += str(map_field) + ", "
        s = "<%s: Fields = %s>"%(self.__class__.__name__, map_str)
        return s

    def __repr__(self):
        return self.__str__()

class MapField(object):
    def __init__(self, name, word_index, num_bits, bit_offset):
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self._word_index = word_index
        self._num_bits = num_bits
        self._name = name
        self._bit_offset = bit_offset
        self._value = None
    
    @property
    def num_bits(self):
        return self._num_bits
    
    @property
    def bit_offset(self):
        return self._bit_offset
    
    @property
    def name(self):
        return self._name
    
    @property
    def word_index(self):
        return self._word_index
    
    @property
    def mask(self):
        return (2**self._num_bits -1) << self._bit_offset
    
    @property
    def value(self):
        self.log.debug("getting value = %s", str(self._value))
        return self._value
    @value.setter
    def value(self, value):
        self.log.debug("setting value = %s (was = %s)", str(value), str(self._value))
        self._value = value
    
    def extract_field_value(self, words):
        self._value = (words[self._word_index] & self.mask) >> self._bit_offset
        return self._value
    
    def insert_field_value(self, words):
        # Clear the relevant bits in the input word (AND with an inverted mask)
        # Then set the relevant bit values (value shifted up and OR'ed)
        if self._value == None:
            raise_with_traceback(ValueError("No value initialised for field: \'%s\'"%self._name))
        words[self._word_index] = (words[self._word_index] & (self.mask ^ 2**32-1)) | (self._value << self._bit_offset)
    
    def __repr__(self):
        s = "<MapField: \"%s\" word:%i offset:%i bits:%i val:%s>"%(self._name,
                                                                 self._word_index,
                                                                 self._bit_offset,
                                                                 self._num_bits,
                                                                 str(self._value))
        return s
    
    def __str__(self):
        s = "<%s=%s>"%(self._name, str(self._value))
        return s

class HeaderInfo(DeviceSettings):
    """Represent the Header Info register bank"""
    num_words = 1
    def __init__(self):
        object.__setattr__(self, '_mem_map', {}) # This prevents infinite recursion when setting attributes
        self._mem_map = {"eeprom_address":               MapField("eeprom_address",              0, 8, 16),
                    "monitoring_channels_count":    MapField("monitoring_channels_count",   0, 8,  8),
                    "control_channels_count":       MapField("control_channels_count",      0, 8,  0),
                    }

class ControlChannel(DeviceSettings):
    """Represent the map of Control Channels register bank"""
    num_words = 4
    def __init__(self):
        object.__setattr__(self, '_mem_map', {}) # This prevents infinite recursion when setting attributes
        self._mem_map = {"board_type":                   MapField("board_type",                  0,  3, 24),
                    "component_family_id":          MapField("component_family_id",         0,  4, 20),
                    "device_i2c_bus_select":        MapField("device_i2c_bus_select",       0,  2, 18),
                    "channel_device_id":            MapField("channel_device_id",           0,  5, 13),
                    "channel_sub_address":          MapField("channel_sub_address",         0,  5,  8),
                    "device_address":               MapField("device_address",              0,  8,  0), 
                    
                    "channel_range_max":            MapField("channel_range_max",           1, 16, 16),
                    "channel_range_min":            MapField("channel_range_min",           1, 16,  0),
                    
                    "channel_default_on":           MapField("channel_default_on",          2, 16, 16),
                    "channel_default_off":          MapField("channel_default_off",         2, 16,  0),
                    
                    # These are not yet in use
                    #"channel_monitoring":           MapField("channel_monitoring",          3,  8, 16),
                    #"safety_exception_threshold":   MapField("safety_exception_threshold",  3,  8,  8),
                    #"read_frequency":               MapField("read_frequency",              3,  8,  0),
    
                    "power_status":                 MapField("power_status",                3,  1, 16),
                    "value":                        MapField("value",                       3, 16,  0),
                    }

        
class MonitoringChannel(DeviceSettings):
    """Represent the map of Monitoring Channel register bank"""
    num_words = 4
    def __init__(self):
        object.__setattr__(self, '_mem_map', {}) # This prevents infinite recursion when setting attributes
        self._mem_map = {"board_type":                   MapField("board_type",                  0,  3, 24),
                    "component_family_id":          MapField("component_family_id",         0,  4, 20),
                    "device_i2c_bus_select":        MapField("device_i2c_bus_select",       0,  2, 18),
                    "channel_device_id":            MapField("channel_device_id",           0,  5, 13),
                    "channel_sub_address":          MapField("channel_sub_address",         0,  5,  8),
                    "device_address":               MapField("device_address",              0,  8,  0), 
                    
                    "channel_ext_low_threshold":    MapField("channel_ext_low_threshold",   1, 16, 16),
                    "channel_ext_high_threshold":   MapField("channel_ext_high_threshold",  1, 16,  0),
                    
                    "channel_low_threshold":        MapField("channel_low_threshold",       2, 16, 16),
                    "channel_high_threshold":       MapField("channel_high_threshold",      2, 16,  0),
                    
                    "channel_monitoring":           MapField("channel_monitoring",          3,  8, 16),
                    "safety_exception_threshold":   MapField("safety_exception_threshold",  3,  8,  8),
                    "read_frequency":               MapField("read_frequency",              3,  8,  0),
                    }
    
class Command(DeviceSettings):
    """Represent the Command register bank:
    
        * Word 0: Device command interface word
        * Word 1: Sensor command interface word
        * Word 2: System command interface word
    """
    num_words = 3
    def __init__(self):
        object.__setattr__(self, '_mem_map', {}) # This prevents infinite recursion when setting attributes
        self._mem_map = {"device_cmd":                   MapField("device_cmd",                   0,  3, 28),
                         "device_type":                  MapField("device_type",                  0,  2, 23),
                         #"eeprom_target":                MapField("eeprom_target",                0,  3, 25),
                         "device_index":                 MapField("device_index",                 0, 16,  0),
                
                         "sensor_cmd":                   MapField("sensor_cmd",                   1, 16, 16),
                         "sensor_cmd_data":              MapField("sensor_cmd_data",              1, 16,  0),
                
                         "system_cmd":                   MapField("system_cmd",                   2, 16, 16),
                         "system_cmd_data":              MapField("system_cmd_data",              2, 16,  0),
                         }

class EchoWord(DeviceSettings):
    """Represent the ECHO WORD register bank of just one single word
    """
    num_words = 1
    def __init__(self):
        object.__setattr__(self, '_mem_map', {}) # This prevents infinite recursion when setting attributes
        self._mem_map = {"read_value":                   MapField("read_value",                   0,  16,  0),
                         "i2c_communication_error":      MapField("i2c_communication_error",      0,   1, 16),
                         }

class ReadValue(DeviceSettings):
    """Represent the READ VALUE register bank of just one single word
    """
    num_words = 1
    def __init__(self):
        object.__setattr__(self, '_mem_map', {}) # This prevents infinite recursion when setting attributes
        self._mem_map = {"read_value":                   MapField("read_value",                   0,  16,  0),
                         "i2c_communication_error":      MapField("i2c_communication_error",      0,   1, 16),
                         "safety_exception_detected":    MapField("safety_exception_detected",    0,   1, 17),
                         "below_extreme_low_threshold":  MapField("below_extreme_low_threshold",  0,   1, 18),
                         "below_low_threshold":          MapField("below_low_threshold",          0,   1, 19),
                         "above_high_threshold":         MapField("above_high_threshold",         0,   1, 20),
                         "above_extreme_high_threshold": MapField("above_extreme_high_threshold", 0,   1, 21),
                         "sample_number":                MapField("sample_number",                0,   8, 24),
                         }


class IDeviceSettings(with_metaclass(abc.ABCMeta, IABCMeta)):
    '''
    Interface to a Device Setting bitmap.
    '''
    __iproperties__ = ['num_words']
    __imethods__ = ['parse_map', 'parse_map_from_tuples', 'generate_map']
    _iface_requirements = __imethods__ + __iproperties__
    
    @abc.abstractproperty
    def num_words(self):
        """Number of 32bit words in the bitmap"""
        raise NotImplementedError
    
    @abc.abstractproperty
    def _mem_map(self):
        """Internal (private) logical representation of the bitmap
            
            Must be a dictionary of :class:`MapField` objects
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    def parse_map(self, words):
        """Parse a list of words as a bitmap and write to the relevant internal MapFields

            :param words: 32 bit integer words
            :type  words: list"""
        raise NotImplementedError

    @abc.abstractmethod
    def parse_map_from_tuples(self, tuples):
        """Parse a list of words as a bitmap and write to the relevant internal MapFields

            :param tuples: List of tuples with (address, value) where address is 16bit and value is 32 bit integer words
            :type  tuples: list"""
        raise NotImplementedError

    @abc.abstractmethod
    def generate_map(self):
        """Generate a bitmap from the device MapFields. 
        
            :returns: a list of 32bit words"""
        raise NotImplementedError
    

       
IDeviceSettings.register(HeaderInfo)
IDeviceSettings.register(ControlChannel)
IDeviceSettings.register(MonitoringChannel)

