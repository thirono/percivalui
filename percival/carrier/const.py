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

FIRMWARE_VERSION = "2017.01.24"
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
CONTROL_SETTINGS_LEFT = UARTBlock(1, 4, 0x0001)
MONITORING_SETTINGS_LEFT = UARTBlock(1, 4, 0x0005)
HEADER_SETTINGS_BOTTOM = UARTBlock(1, 1, 0x0009)
CONTROL_SETTINGS_BOTTOM = UARTBlock(1, 4, 0x000A)
MONITORING_SETTINGS_BOTTOM = UARTBlock(1, 4, 0x000E)
HEADER_SETTINGS_CARRIER = UARTBlock(1, 1, 0x0012)
CONTROL_SETTINGS_CARRIER = UARTBlock(14, 4, 0x0013)
MONITORING_SETTINGS_CARRIER = UARTBlock(19, 4, 0x004B)
HEADER_SETTINGS_PLUGIN = UARTBlock(1, 1, 0x0097)
CONTROL_SETTINGS_PLUGIN = UARTBlock(1, 4, 0x0098)
MONITORING_SETTINGS_PLUGIN = UARTBlock(1, 4, 0x009C)
CHIP_READOUT_SETTINGS = UARTBlock(1, 32, 0x00A0)
CLOCK_SETTINGS = UARTBlock(1, 8, 0x00C0)
SYSTEM_SETTINGS = UARTBlock(1, 18, 0x00C8)
SAFETY_SETTINGS = UARTBlock(1, 8, 0x00DA)
WRITE_BUFFER = UARTBlock(1, 64, 0x00E2)
COMMAND = UARTBlock(1, 3, 0x0122)
READ_VALUES_PERIPHERY_LEFT = UARTBlock(1, 1, 0x0125)
READ_VALUES_PERIPHERY_BOTTOM = UARTBlock(1, 1, 0x0126)
READ_VALUES_CARRIER = UARTBlock(19, 1, 0x0127)
READ_VALUES_PLUGIN = UARTBlock(1, 1, 0x013A)
READ_VALUES_STATUS = UARTBlock(1, 8, 0x013B)
READ_BUFFER = UARTBlock(1, 64, 0x0143)
READ_ECHO_WORD = UARTBlock(1, 1, 0x0183)
READBACK_HEADER_SETTINGS_LEFT = UARTBlock(1, 1, 0x0184)
READBACK_CONTROL_SETTINGS_LEFT = UARTBlock(1, 1, 0x0185)
READBACK_MONITORING_SETTINGS_LEFT = UARTBlock(1, 1, 0x0186)
READBACK_HEADER_SETTINGS_BOTTOM = UARTBlock(1, 1, 0x0187)
READBACK_CONTROL_SETTINGS_BOTTOM = UARTBlock(1, 1, 0x0188)
READBACK_MONITORING_SETTINGS_BOTTOM = UARTBlock(1, 1, 0x0189)
READBACK_HEADER_SETTINGS_CARRIER = UARTBlock(1, 1, 0x018A)
READBACK_CONTROL_SETTINGS_CARRIER = UARTBlock(1, 1, 0x018B)
READBACK_MONITORING_SETTINGS_CARRIER = UARTBlock(1, 1, 0x018C)
READBACK_HEADER_SETTINGS_PLUGIN = UARTBlock(1, 1, 0x018D)
READBACK_CONTROL_SETTINGS_PLUGIN = UARTBlock(1, 1, 0x018E)
READBACK_MONITORING_SETTINGS_PLUGIN = UARTBlock(1, 1, 0x018F)
READBACK_CHIP_READOUT_SETTINGS = UARTBlock(1, 1, 0x0190)
READBACK_CLOCK_SETTINGS = UARTBlock(1, 1, 0x0191)
READBACK_SYSTEM_SETTINGS = UARTBlock(1, 1, 0x0192)
READBACK_SAFETY_SETTINGS = UARTBlock(1, 1, 0x0193)
READBACK_WRITE_BUFFER = UARTBlock(1, 1, 0x0194)
READBACK_READ_VALUES_PERIPHERY_LEFT = UARTBlock(1, 1, 0x0195)
READBACK_READ_VALUES_PERIPHERY_BOTTOM = UARTBlock(1, 1, 0x0196)
READBACK_READ_VALUES_CARRIER = UARTBlock(1, 1, 0x0197)
READBACK_READ_VALUES_PLUGIN = UARTBlock(1, 1, 0x0198)
READBACK_READ_VALUES_STATUS = UARTBlock(1, 1, 0x0199)
READBACK_READ_BUFFER = UARTBlock(1, 1, 0x019A)
READBACK_READ_ECHO_WORD = UARTBlock(1, 1, 0x019B)


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
    enable_level_safety_controls = 5
    disable_level_safety_controls = 6
    enable_experimental_level_safety_controls = 7
    disable_experimental_level_safety_controls = 8
    enable_safety_actions = 9
    disable_safety_actions = 10
    enter_acquisition_armed_status = 11
    exit_acquisition_armed_status = 12
    start_acquisition = 13
    stop_acquisition = 14
    fast_sensor_powerup = 15
    fast_sensor_powerdown = 16
    fast_enable_control_standby = 17
    fast_disable_control_standby = 18
    enable_startup_mode = 19
    disable_startup_mode = 20
		   
		   
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