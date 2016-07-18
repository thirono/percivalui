"""
Definitions of the Carrier Board UART control registers

Update this whenever there are any firmware/documentation changes to register map definitions in the UART blocks.
"""

from __future__ import unicode_literals, absolute_import

from future.utils import with_metaclass, raise_with_traceback
from builtins import range
import abc

from percival.detector.interface import IABCMeta
from . import encoding, const
from percival.carrier import txrx
import logging

logger = logging.getLogger(__name__)


class RegisterMap(object):
    """Mixin to be used by classes that implement the `IRegisterMap` interface"""
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

    def __getitem__(self, item):
        return self._mem_map[item]

    def parse_map(self, words):
        if len(words) != self.num_words:
            raise_with_traceback(IndexError("Map must contain %d words. Got only %d" % (self.num_words, len(words))))
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

    @property
    def map_fields(self):
        return self._mem_map.keys()

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
    """
    Store the information required to parse a value out of a specific field in a register map

     * Word index
     * Number of bits
     * Value bit offset within the word
    """
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

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)


class HeaderInfoMap(RegisterMap):
    """Represent the Header Info register bank"""
    num_words = 1

    def __init__(self):
        object.__setattr__(self, '_mem_map', {}) # This prevents infinite recursion when setting attributes
        self._mem_map = {"eeprom_address":               MapField("eeprom_address",              0, 8, 16),
                         "monitoring_channels_count":    MapField("monitoring_channels_count",   0, 8,  8),
                         "control_channels_count":       MapField("control_channels_count",      0, 8,  0),
                         }


class ControlChannelMap(RegisterMap):
    """Represent the map of Control Channels register bank"""
    num_words = 4

    def __init__(self):
        object.__setattr__(self, '_mem_map', {}) # This prevents infinite recursion when setting attributes
        self._mem_map = {"channel_id":                   MapField("channel_id",                  0,  5, 27),
                         "board_type":                   MapField("board_type",                  0,  3, 24),
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


class MonitoringChannelMap(RegisterMap):
    """Represent the map of Monitoring Channel register bank"""
    num_words = 4

    def __init__(self):
        object.__setattr__(self, '_mem_map', {}) # This prevents infinite recursion when setting attributes
        self._mem_map = {"channel_id":                   MapField("channel_id",                  0,  5, 27),
                         "board_type":                   MapField("board_type",                  0,  3, 24),
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


class CommandMap(RegisterMap):
    """Represent the CommandMap register bank:

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

                         "buffer_cmd_destination":       MapField("buffer_cmd_destination",       1,  4, 28),
                         "buffer_cmd":                   MapField("buffer_cmd",                   1,  4, 24),
                         "buffer_cmd_words":             MapField("buffer_cmd_words",             1,  8, 16),
                         "buffer_cmd_address":           MapField("buffer_cmd_address",           1, 16,  0),

                         "system_cmd":                   MapField("system_cmd",                   2, 16, 16),
                         "system_cmd_data":              MapField("system_cmd_data",              2, 16,  0),
                         }


class EchoWordMap(RegisterMap):
    """Represent the ECHO WORD register bank of just one single word
    """
    num_words = 1

    def __init__(self):
        object.__setattr__(self, '_mem_map', {}) # This prevents infinite recursion when setting attributes
        self._mem_map = {"read_value":                   MapField("read_value",                   0,  16,  0),
                         "i2c_communication_error":      MapField("i2c_communication_error",      0,   1, 16),
                         "sample_number":                MapField("sample_number",                0,   8, 24),
                         }


class ReadValueMap(RegisterMap):
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


class IRegisterMap(with_metaclass(abc.ABCMeta, IABCMeta)):
    """
    Interface to a Device Setting bitmap.
    """
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


IRegisterMap.register(HeaderInfoMap)
IRegisterMap.register(ControlChannelMap)
IRegisterMap.register(MonitoringChannelMap)


RegisterMapClasses = {
    const.RegisterMapType.header:     HeaderInfoMap,
    const.RegisterMapType.control:    ControlChannelMap,
    const.RegisterMapType.monitoring: MonitoringChannelMap,
    const.RegisterMapType.command:    CommandMap
}

BoardRegisters = {
    #                          header,                        control,                        monitoring
    const.BoardTypes.left:    (const.HEADER_SETTINGS_LEFT,    const.CONTROL_SETTINGS_LEFT,    const.MONITORING_SETTINGS_LEFT),
    const.BoardTypes.bottom:  (const.HEADER_SETTINGS_BOTTOM,  const.CONTROL_SETTINGS_BOTTOM,  const.MONITORING_SETTINGS_BOTTOM),
    const.BoardTypes.carrier: (const.HEADER_SETTINGS_CARRIER, const.CONTROL_SETTINGS_CARRIER, const.MONITORING_SETTINGS_CARRIER),
    const.BoardTypes.plugin:  (const.HEADER_SETTINGS_PLUGIN,  const.CONTROL_SETTINGS_PLUGIN,  const.MONITORING_SETTINGS_PLUGIN),
}

BoardValueRegisters = {
    const.BoardTypes.left: const.READ_VALUES_PERIPHERY_LEFT,
    const.BoardTypes.bottom: const.READ_VALUES_PERIPHERY_BOTTOM,
    const.BoardTypes.carrier: const.READ_VALUES_CARRIER,
    const.BoardTypes.plugin: const.READ_VALUES_PLUGIN
}

# Each entry is a tuple of:     (description,                 read_addr, entries, words, RegisterMap subclass)
CarrierUARTRegisters = {
    const.HEADER_SETTINGS_LEFT:         ("Header settings left",        const.READBACK_HEADER_SETTINGS_LEFT,         HeaderInfoMap),
    const.CONTROL_SETTINGS_LEFT:        ("Control settings left",       const.READBACK_CONTROL_SETTINGS_LEFT,        ControlChannelMap),
    const.MONITORING_SETTINGS_LEFT:     ("Monitoring settings left",    const.READBACK_MONITORING_SETTINGS_LEFT,     MonitoringChannelMap),
    const.READ_VALUES_PERIPHERY_LEFT:   ("Read monitor values left",    const.READBACK_READ_VALUES_PERIPHERY_LEFT,   ReadValueMap),
    const.HEADER_SETTINGS_BOTTOM:       ("Header settings bottom",      const.READBACK_HEADER_SETTINGS_BOTTOM,       HeaderInfoMap),
    const.CONTROL_SETTINGS_BOTTOM:      ("Control settings bottom",     const.READBACK_CONTROL_SETTINGS_BOTTOM,      ControlChannelMap),
    const.MONITORING_SETTINGS_BOTTOM:   ("Monitoring settings bottom",  const.READBACK_MONITORING_SETTINGS_BOTTOM,   MonitoringChannelMap),
    const.READ_VALUES_PERIPHERY_BOTTOM: ("Read monitor values bottom",  const.READBACK_READ_VALUES_PERIPHERY_BOTTOM, ReadValueMap),
    const.HEADER_SETTINGS_CARRIER:      ("Header settings carrier",     const.READBACK_HEADER_SETTINGS_BOTTOM,       HeaderInfoMap),
    const.CONTROL_SETTINGS_CARRIER:     ("Control settings carrier",    const.READBACK_CONTROL_SETTINGS_CARRIER,     ControlChannelMap),
    const.MONITORING_SETTINGS_CARRIER:  ("Monitoring settings carrier", const.READBACK_MONITORING_SETTINGS_CARRIER,  MonitoringChannelMap),
    const.READ_VALUES_CARRIER:          ("Read monitor values carrier", const.READBACK_READ_VALUES_CARRIER,          ReadValueMap),
    const.HEADER_SETTINGS_PLUGIN:       ("Header settings plugin",      const.READBACK_HEADER_SETTINGS_PLUGIN,       HeaderInfoMap),
    const.CONTROL_SETTINGS_PLUGIN:      ("Control settings plugin",     const.READBACK_CONTROL_SETTINGS_PLUGIN,      ControlChannelMap),
    const.MONITORING_SETTINGS_PLUGIN:   ("Monitoring settings plugin",  const.READBACK_MONITORING_SETTINGS_PLUGIN,   MonitoringChannelMap),
    const.READ_VALUES_PLUGIN:           ("Read monitor values plugin",  const.READBACK_READ_VALUES_PLUGIN,           ReadValueMap),
    const.COMMAND:                      ("CommandMap",                  None,                                        CommandMap),
    const.READ_ECHO_WORD:               ("Read Echo Word",              const.READBACK_READ_ECHO_WORD,               EchoWordMap),
}
"""Look-up table of UART addresses and the corresponding details

        The key is the UART write address :obj:`percival.carrier.const.UARTBlock` and each item is a tuple of:

        * description
        * UART read_addr :obj:`percival.carrier.const.UARTBlock`
        * Corresponding implementation of the :class:`percival.carrier.devices.IRegisterMap` interface
"""


class UARTRegister(object):
    ''' Represent a specific UART register on the Percival Carrier Board
    '''
    UART_ADDR_WIDTH = 16
    UART_WORD_WIDTH = 32

    def __init__(self, uart_block, uart_device=None):
        '''Constructor
        
            :param uart_block: UART start address for a block of registers.
                This is used as a look-up key to the functionality of that register in the CarrierUARTRegisters dictionary
            :type  uart_block: :obj:`percival.carrier.const.UARTBlock`
            :param uart_device: UART start address for a specific device within the register block. If defined
                this will be used to generate write commands in get_write_cmd_msg().
            :type uart_device: int
        '''
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        (self._name, self._readback_addr, DeviceClass) = CarrierUARTRegisters[uart_block]
        self._uart_block_address = uart_block
        self._uart_address = uart_block.start_address
        self.log.debug("UARTRegister _uart_address: %02X", self._uart_address)

        self.fields = None  # A devices.RegisterMap object
        if DeviceClass:
            self.fields = DeviceClass()

        if uart_device:
            self._uart_address = uart_device
            self.log.debug("UARTRegister updated _uart_address: %02X", self._uart_address)
            if uart_device.bit_length() > self.UART_ADDR_WIDTH:
                raise_with_traceback(ValueError("UART device address value 0x%H is greater than 16 bits" %
                                                uart_device))

        if uart_block.start_address.bit_length() > self.UART_ADDR_WIDTH:
            raise_with_traceback(ValueError("UART block address value 0x%H is greater than 16 bits" %
                                            uart_block.start_address))
        if self._readback_addr:
            if self._readback_addr.start_address.bit_length() > self.UART_ADDR_WIDTH:
                raise_with_traceback(ValueError("readback_addr value 0x%H is greater than 16 bits" %
                                                self._readback_addr.start_address))

    @property
    def words_per_item(self):
        return self._uart_block_address.words_per_entry

    @property
    def num_items(self):
        return self._uart_block_address.entries

    def initialize_map(self, register_map):
        if len(register_map) >= 1:
            if type(register_map[0]) == int:
                self.fields.parse_map(register_map)
            elif type(register_map[0]) == tuple:
                self.fields.parse_map_from_tuples(register_map)
            else:
                raise_with_traceback(TypeError("register_map must be list/tuple of type int or tuple"))
        else:
            raise_with_traceback("Cannot initialize register map with an empty container")
       
    def get_read_cmd_msg(self):
        """Generate a message to do a readback (shortcut) command of the current register map
        
            :returns: A read UART command message
            :rtype:  list of :class:`percival.carrier.txrx.TxMessage` objects
        """
        if not self._readback_addr:
            raise_with_traceback( TypeError("A readback shortcut is not available for \'%s\'"%self._name) )
        read_cmd_msg = encoding.encode_message(self._readback_addr.start_address, 0x00000000)
        self.log.debug(read_cmd_msg)
        return txrx.TxMessage(read_cmd_msg, self.words_per_item * self.num_items)
    
    def get_write_cmd_msg(self, eom=False):
        """Flatten the 2D matrix of datawords into one continuous list
        
            :returns: A write UART command message
            :rtype:  list of :class:`percival.carrier.txrx.TxMessage` objects"""
        data_words = self.fields.generate_map()
        write_cmd_msg = encoding.encode_multi_message(self._uart_address, data_words)
        write_cmd_msg = [txrx.TxMessage(msg, num_response_msg=1, expect_eom=eom) for msg in write_cmd_msg]
        return write_cmd_msg


def get_register_block(addr):
    """Scan through the top-level register blocks to find the block addr belongs in.

    :param addr: UART address
    :type addr: int
    :return: Return the address block if found or None if addr is out of range
    :rtype: :obj:`percival.carrier.const.UARTBlock`
    """
    register_blocks = CarrierUARTRegisters.keys()
    for register_block in register_blocks:
        if register_block.start_address <= \
           addr < \
           (register_block.start_address + (register_block.entries * register_block.words_per_entry)):
            return register_block


def generate_register_maps(registers):
    """Provides the connection between raw register maps: list of (addr, data) tuples and
    :class:`percival.carrier.registers.RegisterMap` implementations.

    :param registers: List of (addr, data) register tuples
    :type registers: list
    :returns: A list of :class:`RegisterMap` objects
    :rtype: list
    """
    index = 0
    register_maps = []
    while index < len(registers):
        addr, data = registers[index]
        uart_block = get_register_block(addr)
        if not uart_block:
            logger.warning("Did not find UART block for address: 0x%X", addr)
            index += 1
            continue
        if ((addr - uart_block.start_address) % uart_block.words_per_entry) != 0:
            logger.warning("UART address %s doesn't align with element boundary within the block %s.", addr, uart_block)
            index += 1
            continue
        (name, readback_addr_block, RegisterMapClass) = CarrierUARTRegisters[uart_block]
        block_map = RegisterMapClass()
        block_words = registers[index:index + block_map.num_words]
        try:
            block_map.parse_map_from_tuples(block_words)
        except IndexError as e:
            logger.warning("Register map length issue: %s", str(e))
            index += 1
            continue

        register_maps.append(block_map)
        index += block_map.num_words
    return register_maps

