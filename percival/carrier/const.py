"""
Constants and enumerations for the Carrier Board firmware as defined in documentation
"""
from __future__ import unicode_literals, absolute_import

from enum import Enum, unique

FIRMWARE_VERSION = "2016.04.20"


class UARTBlocks(object):
    def __init__(self, entries, words_per_entry, start_address):
        self.entries = entries
        self.words_per_entry = words_per_entry
        self.start_address = start_address


HEADER_SETTINGS_LEFT = UARTBlocks(1, 1, 0x0000)
CONTROL_SETTINGS_LEFT = UARTBlocks(1, 4, 0x0001)
MONITORING_SETTINGS_LEFT = UARTBlocks(1, 4, 0x0005)
HEADER_SETTINGS_BOTTOM = UARTBlocks(1, 1, 0x0009)
CONTROL_SETTINGS_BOTTOM = UARTBlocks(1, 4, 0x000A)
MONITORING_SETTINGS_BOTTOM = UARTBlocks(1, 4, 0x000E)
HEADER_SETTINGS_CARRIER = UARTBlocks(1, 1, 0x0012)
CONTROL_SETTINGS_CARRIER = UARTBlocks(14, 4, 0x0013)
MONITORING_SETTINGS_CARRIER = UARTBlocks(19, 4, 0x004B)
HEADER_SETTINGS_PLUGIN = UARTBlocks(1, 1, 0x0097)
CONTROL_SETTINGS_PLUGIN = UARTBlocks(1, 4, 0x0098)
MONITORING_SETTINGS_PLUGIN = UARTBlocks(1, 4, 0x009C)
CHIP_READOUT_SETTINGS = UARTBlocks(1, 32, 0x00A0)
CLOCK_SETTINGS = UARTBlocks(1, 8, 0x00C0)
SYSTEM_SETTINGS = UARTBlocks(1, 8, 0x00C8)
SAFETY_SETTINGS = UARTBlocks(2, 8, 0x00D0)
WRITE_BUFFER = UARTBlocks(1, 32, 0x00D8)
COMMAND = UARTBlocks(1, 3, 0x00F8)
READ_VALUES_PERIPHERY_LEFT = UARTBlocks(1, 1, 0x00FB)
READ_VALUES_PERIPHERY_BOTTOM = UARTBlocks(1, 1, 0x00FC)
READ_VALUES_CARRIER = UARTBlocks(19, 1, 0x00FD)
READ_VALUES_PLUGIN = UARTBlocks(1, 1, 0x0110)
READ_VALUES_STATUS = UARTBlocks(1, 8, 0x0111)
READ_BUFFER = UARTBlocks(1, 32, 0x0119)
READ_ECHO_WORD = UARTBlocks(1, 1, 0x0139)
READBACK_HEADER_SETTINGS_LEFT = UARTBlocks(1, 1, 0x013A)
READBACK_CONTROL_SETTINGS_LEFT = UARTBlocks(1, 1, 0x013B)
READBACK_MONITORING_SETTINGS_LEFT = UARTBlocks(1, 1, 0x013C)
READBACK_HEADER_SETTINGS_BOTTOM = UARTBlocks(1, 1, 0x013D)
READBACK_CONTROL_SETTINGS_BOTTOM = UARTBlocks(1, 1, 0x013E)
READBACK_MONITORING_SETTINGS_BOTTOM = UARTBlocks(1, 1, 0x013F)
READBACK_HEADER_SETTINGS_CARRIER = UARTBlocks(1, 1, 0x0140)
READBACK_CONTROL_SETTINGS_CARRIER = UARTBlocks(1, 1, 0x0141)
READBACK_MONITORING_SETTINGS_CARRIER = UARTBlocks(1, 1, 0x0142)
READBACK_HEADER_SETTINGS_PLUGIN = UARTBlocks(1, 1, 0x0143)
READBACK_CONTROL_SETTINGS_PLUGIN = UARTBlocks(1, 1, 0x0144)
READBACK_MONITORING_SETTINGS_PLUGIN = UARTBlocks(1, 1, 0x0145)
READBACK_CHIP_READOUT_SETTINGS = UARTBlocks(1, 1, 0x0146)
READBACK_CLOCK_SETTINGS = UARTBlocks(1, 1, 0x0147)
READBACK_SYSTEM_SETTINGS = UARTBlocks(1, 1, 0x0148)
READBACK_SAFETY_SETTINGS = UARTBlocks(1, 1, 0x0149)
READBACK_WRITE_BUFFER = UARTBlocks(1, 1, 0x014A)
READBACK_READ_VALUES_PERIPHERY_LEFT = UARTBlocks(1, 1, 0x014B)
READBACK_READ_VALUES_PERIPHERY_BOTTOM = UARTBlocks(1, 1, 0x014C)
READBACK_READ_VALUES_CARRIER = UARTBlocks(1, 1, 0x014D)
READBACK_READ_VALUES_PLUGIN = UARTBlocks(1, 1, 0x014E)
READBACK_READ_VALUES_STATUS = UARTBlocks(1, 1, 0x014F)
READBACK_READ_BUFFER = UARTBlocks(1, 1, 0x0150)
READBACK_READ_ECHO_WORD = UARTBlocks(1, 1, 0x0151)


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


