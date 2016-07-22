"""
Constants and enumerations for the Carrier Board firmware as defined in documentation.

Update this whenever there are any firmware/documentation changes regarding:

 * UART address space
 * Enumerations of:

  - Device families
  - Device functions
  - Device or system commands
  - Board types

 * Firmware version: :obj:`FIRMWARE_VERSION`
"""

from __future__ import unicode_literals, absolute_import

from enum import Enum, unique

FIRMWARE_VERSION = "2016.06.30"
"""Elettra Firmware version is based on date"""


class UARTBlock(object):
    """
    Representation of a UART block of registers:

    * Start address
    * Number of elements (entries) in the block
    * Number of words per element (entry) in the block
    """
    def __init__(self, entries, words_per_entry, start_address):
        self.entries = entries
        self.words_per_entry = words_per_entry
        self.start_address = start_address

    def is_address_valid(self, address):
        return self.start_address <= address < (self.start_address + self.words_per_entry * self.entries)


HEADER_SETTINGS_LEFT = UARTBlock(1, 1, 0x0000)
CONTROL_SETTINGS_LEFT = UARTBlock(16, 4, 0x0001)
MONITORING_SETTINGS_LEFT = UARTBlock(16, 4, 0x0041)
HEADER_SETTINGS_BOTTOM = UARTBlock(1, 1, 0x0081)
CONTROL_SETTINGS_BOTTOM = UARTBlock(2, 4, 0x0082)
MONITORING_SETTINGS_BOTTOM = UARTBlock(2, 4, 0x008A)
HEADER_SETTINGS_CARRIER = UARTBlock(1, 1, 0x0092)
CONTROL_SETTINGS_CARRIER = UARTBlock(14, 4, 0x0093)
MONITORING_SETTINGS_CARRIER = UARTBlock(19, 4, 0x00CB)
HEADER_SETTINGS_PLUGIN = UARTBlock(1, 1, 0x0117)
CONTROL_SETTINGS_PLUGIN = UARTBlock(2, 4, 0x0118)
MONITORING_SETTINGS_PLUGIN = UARTBlock(2, 4, 0x0120)
CHIP_READOUT_SETTINGS = UARTBlock(1, 32, 0x0128)
CLOCK_SETTINGS = UARTBlock(1, 8, 0x0148)
SYSTEM_SETTINGS = UARTBlock(1, 8, 0x0150)
SAFETY_SETTINGS = UARTBlock(2, 8, 0x0158)
WRITE_BUFFER = UARTBlock(1, 16, 0x0160)
COMMAND = UARTBlock(1, 3, 0x0170)
READ_VALUES_PERIPHERY_LEFT = UARTBlock(16, 1, 0x0173)
READ_VALUES_PERIPHERY_BOTTOM = UARTBlock(2, 1, 0x0183)
READ_VALUES_CARRIER = UARTBlock(19, 1, 0x0185)
READ_VALUES_PLUGIN = UARTBlock(2, 1, 0x0198)
READ_VALUES_STATUS = UARTBlock(1, 8, 0x019A)
READ_BUFFER = UARTBlock(1, 16, 0x01A2)
READ_ECHO_WORD = UARTBlock(1, 1, 0x01B2)
READBACK_HEADER_SETTINGS_LEFT = UARTBlock(1, 1, 0x01B3)
READBACK_CONTROL_SETTINGS_LEFT = UARTBlock(1, 1, 0x01B4)
READBACK_MONITORING_SETTINGS_LEFT = UARTBlock(1, 1, 0x01B5)
READBACK_HEADER_SETTINGS_BOTTOM = UARTBlock(1, 1, 0x01B6)
READBACK_CONTROL_SETTINGS_BOTTOM = UARTBlock(1, 1, 0x01B7)
READBACK_MONITORING_SETTINGS_BOTTOM = UARTBlock(1, 1, 0x01B8)
READBACK_HEADER_SETTINGS_CARRIER = UARTBlock(1, 1, 0x01B9)
READBACK_CONTROL_SETTINGS_CARRIER = UARTBlock(1, 1, 0x01BA)
READBACK_MONITORING_SETTINGS_CARRIER = UARTBlock(1, 1, 0x01BB)
READBACK_HEADER_SETTINGS_PLUGIN = UARTBlock(1, 1, 0x01BC)
READBACK_CONTROL_SETTINGS_PLUGIN = UARTBlock(1, 1, 0x01BD)
READBACK_MONITORING_SETTINGS_PLUGIN = UARTBlock(1, 1, 0x01BE)
READBACK_CHIP_READOUT_SETTINGS = UARTBlock(1, 1, 0x01BF)
READBACK_CLOCK_SETTINGS = UARTBlock(1, 1, 0x01C0)
READBACK_SYSTEM_SETTINGS = UARTBlock(1, 1, 0x01C1)
READBACK_SAFETY_SETTINGS = UARTBlock(1, 1, 0x01C2)
READBACK_WRITE_BUFFER = UARTBlock(1, 1, 0x01C3)
READBACK_READ_VALUES_PERIPHERY_LEFT = UARTBlock(1, 1, 0x01C4)
READBACK_READ_VALUES_PERIPHERY_BOTTOM = UARTBlock(1, 1, 0x01C5)
READBACK_READ_VALUES_CARRIER = UARTBlock(1, 1, 0x01C6)
READBACK_READ_VALUES_PLUGIN = UARTBlock(1, 1, 0x01C7)
READBACK_READ_VALUES_STATUS = UARTBlock(1, 1, 0x01C8)
READBACK_READ_BUFFER = UARTBlock(1, 1, 0x01C9)
READBACK_READ_ECHO_WORD = UARTBlock(1, 1, 0x01CA)


@unique
class SystemCmd(Enum):
    """Enumeration of all available system level commands

    This represents the documented "SYSTEM_CMD details"
    """
    no_operation = 0
    enable_global_monitoring = 1
    disable_global_monitoring = 2
    enable_device_level_safety_controls = 3
    disable_device_level_safety_controls = 4
    enable_system_level_safety_controls = 5
    disable_system_level_safety_controls = 6
    enable_experimental_level_safety_controls = 7
    disable_experimental_level_safety_controls = 8
    enable_safety_actions = 9
    disable_safety_actions = 10
    start_acquisition = 11
    stop_acquisition = 12
    fast_sensor_powerup = 13
    fast_sensor_powerdown = 14
    switch_on_mgt_of_mezzanine_board_a = 15
    switch_off_mgt_of_mezzanine_board_a = 16
    switch_on_mgt_of_mezzanine_board_b = 17
    switch_off_mgt_of_mezzanine_board_b = 18
    switch_on_phy_of_mezzanine_board_a = 19
    switch_off_phy_of_mezzanine_board_a = 20


@unique
class BoardTypes(Enum):
    """Enumeration of the board types"

    Current list of board types:

    * `prototype`
    * `left`
    * `bottom`
    * `carrier`
    * `plugin`
    * `other`
    """
    prototype = 0
    left = 1
    bottom = 2
    carrier = 3
    plugin = 4
    other = 5


@unique
class RegisterMapType(Enum):
    header = 0
    control = 1
    monitoring = 2
    command = 3


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
class DeviceFamily(Enum):
    """Enumeration of the available electronic component families"""
    AD5242 = 0
    """Digital potentiometer for control"""
    AD5263 = 1
    """Digital potentiometer for control"""
    AD5629 = 2
    """DAC for control"""
    AD5669 = 3
    """DAC for control"""
    LTC2309 = 7
    """ADC for monitoring"""
    LTC2497 = 4
    """ADC for monitoring"""
    MAX31730 = 5
    """Temperature for monitoring"""
    AT24CM01 = 6
    """EEPROM for on-board configuration storage"""


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


@unique
class BufferTarget(Enum):
    """Enumeration of the BUFFER_TARGET type """
    none = 0
    mezzanine_board_A = 1
    mezzanine_board_B = 2
    both_mezzanine_boards = 3
    plugin_board = 4
    percival_sensor = 5


@unique
class BufferCmd(Enum):
    """Enumeration of buffer commands, not all accepted by all boards """
    no_operation = 0
    write = 1
    read = 2


BufferCommands = {
    BufferTarget.mezzanine_board_A: {
        BufferCmd.no_operation: {"command": int(0), "response": 1},
        BufferCmd.write:        {"command": int(0), "response": 2},
        BufferCmd.read:         {"command": int(1), "response": 2}
                                    },
    BufferTarget.mezzanine_board_B: {
        BufferCmd.no_operation: {"command": int(0), "response": 1},
        BufferCmd.write:        {"command": int(0), "response": 2},
        BufferCmd.read:         {"command": int(1), "response": 2}
                                    },
    BufferTarget.both_mezzanine_boards: {
        BufferCmd.no_operation: {"command": int(0), "response": 1},
        BufferCmd.write:        {"command": int(0), "response": 3}
                                        }
}
