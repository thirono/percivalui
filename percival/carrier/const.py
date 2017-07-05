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

FIRMWARE_VERSION = "2017.05.05"
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
CONTROL_SETTINGS_BOTTOM = UARTBlock(52, 4, 0x000A)
MONITORING_SETTINGS_BOTTOM = UARTBlock(84, 4, 0x00DA)
HEADER_SETTINGS_CARRIER = UARTBlock(1, 1, 0x022A)
CONTROL_SETTINGS_CARRIER = UARTBlock(14, 4, 0x022B)
MONITORING_SETTINGS_CARRIER = UARTBlock(19, 4, 0x0263)
HEADER_SETTINGS_PLUGIN = UARTBlock(1, 1, 0x02AF)
CONTROL_SETTINGS_PLUGIN = UARTBlock(1, 4, 0x02B0)
MONITORING_SETTINGS_PLUGIN = UARTBlock(1, 4, 0x02B4)
CHIP_READOUT_SETTINGS = UARTBlock(1, 32, 0x02B8)
CLOCK_SETTINGS = UARTBlock(1, 8, 0x02D8)
SYSTEM_SETTINGS = UARTBlock(1, 18, 0x02E0)
SAFETY_SETTINGS = UARTBlock(1, 8, 0x02F2)
WRITE_BUFFER = UARTBlock(1, 64, 0x02FA)
COMMAND = UARTBlock(1, 3, 0x033A)
READ_VALUES_PERIPHERY_LEFT = UARTBlock(1, 1, 0x033D)
READ_VALUES_PERIPHERY_BOTTOM = UARTBlock(84, 1, 0x033E)
READ_VALUES_CARRIER = UARTBlock(19, 1, 0x0392)
READ_VALUES_PLUGIN = UARTBlock(1, 1, 0x03A5)
READ_VALUES_STATUS = UARTBlock(1, 8, 0x03A6)
READ_BUFFER = UARTBlock(1, 64, 0x03AE)
READ_ECHO_WORD = UARTBlock(1, 1, 0x03EE)
READBACK_HEADER_SETTINGS_LEFT = UARTBlock(1, 1, 0x03EF)
READBACK_CONTROL_SETTINGS_LEFT = UARTBlock(1, 1, 0x03F0)
READBACK_MONITORING_SETTINGS_LEFT = UARTBlock(1, 1, 0x03F1)
READBACK_HEADER_SETTINGS_BOTTOM = UARTBlock(1, 1, 0x03F2)
READBACK_CONTROL_SETTINGS_BOTTOM = UARTBlock(1, 1, 0x03F3)
READBACK_MONITORING_SETTINGS_BOTTOM = UARTBlock(1, 1, 0x03F4)
READBACK_HEADER_SETTINGS_CARRIER = UARTBlock(1, 1, 0x03F5)
READBACK_CONTROL_SETTINGS_CARRIER = UARTBlock(1, 1, 0x03F6)
READBACK_MONITORING_SETTINGS_CARRIER = UARTBlock(1, 1, 0x03F7)
READBACK_HEADER_SETTINGS_PLUGIN = UARTBlock(1, 1, 0x03F8)
READBACK_CONTROL_SETTINGS_PLUGIN = UARTBlock(1, 1, 0x03F9)
READBACK_MONITORING_SETTINGS_PLUGIN = UARTBlock(1, 1, 0x03FA)
READBACK_CHIP_READOUT_SETTINGS = UARTBlock(1, 1, 0x03FB)
READBACK_CLOCK_SETTINGS = UARTBlock(1, 1, 0x03FC)
READBACK_SYSTEM_SETTINGS = UARTBlock(1, 1, 0x03FD)
READBACK_SAFETY_SETTINGS = UARTBlock(1, 1, 0x03FE)
READBACK_WRITE_BUFFER = UARTBlock(1, 1, 0x03FF)
READBACK_READ_VALUES_PERIPHERY_LEFT = UARTBlock(1, 1, 0x0400)
READBACK_READ_VALUES_PERIPHERY_BOTTOM = UARTBlock(1, 1, 0x0401)
READBACK_READ_VALUES_CARRIER = UARTBlock(1, 1, 0x0402)
READBACK_READ_VALUES_PLUGIN = UARTBlock(1, 1, 0x0403)
READBACK_READ_VALUES_STATUS = UARTBlock(1, 1, 0x0404)
READBACK_READ_BUFFER = UARTBlock(1, 1, 0x0405)
READBACK_READ_ECHO_WORD = UARTBlock(1, 1, 0x0406)


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
    system = 4
    chip_readout = 5


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

@unique
class SensorBufferCmd(Enum):
    """Enumeration of sensor specific buffer commands, only relevant to the sensor """
    no_operation = 0
    send_DACs_setup = 1
    send_CONFIGURATION_setup = 2
    send_CALIBRATION_setup = 3
    send_ROI_setup = 4
    send_DEBUG_setup = 5


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
    },
    BufferTarget.percival_sensor: {
        SensorBufferCmd.no_operation:             {"command": int(0), "response": 1},
        SensorBufferCmd.send_DACs_setup:          {"command": int(0), "response": 1},
        SensorBufferCmd.send_CONFIGURATION_setup: {"command": int(1), "response": 1},
        SensorBufferCmd.send_CALIBRATION_setup:   {"command": int(2), "response": 1},
        SensorBufferCmd.send_ROI_setup:           {"command": int(3), "response": 1},
        SensorBufferCmd.send_DEBUG_setup:         {"command": int(4), "response": 1}
    }
}