'''
Created on 5 Dec 2014

@author: Ulrik Pedersen
'''
from __future__ import unicode_literals, absolute_import
from builtins import range
from enum import Enum, unique

from . import encoding

import logging

from percival.carrier import devices, txrx

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
    left = 0
    bottom = 1
    carrier = 2
    plugin = 3

@unique
class RegisterMapType(Enum):
    header = 0
    control = 1
    monitoring = 2
    command  = 3
    
RegisterMapClasses = {RegisterMapType.header:     devices.HeaderInfo,
                      RegisterMapType.control:    devices.ControlChannel,
                      RegisterMapType.monitoring: devices.MonitoringChannel,
                      RegisterMapType.command:    devices.Command}

BoardRegisters = {BoardTypes.left:    (0x0000, 0x0001, 0x0005),
                  BoardTypes.bottom:  (0x0009, 0x000A, 0x000E),
                  BoardTypes.carrier: (0x0012, 0x0013, 0x004B),
                  BoardTypes.plugin:  (0x0097, 0x0098, 0x009C),
                  }

# Each entry is a tuple of:     (description,                 read_addr, entries, words, DeviceSettings subclass)
CarrierUARTRegisters = {0x0000: ("Header settings left",         0x013A,       1,     1,  devices.HeaderInfo),
                        0x0001: ("Control settings left",        0x013B,       1,     4,  devices.ControlChannel),
                        0x0005: ("Monitoring settings left",     0x013C,       1,     4,  devices.MonitoringChannel),
                        0x0009: ("Header settings bottom",       0x013D,       1,     1,  devices.HeaderInfo),
                        0x000A: ("Control settings bottom",      0x013E,       1,     4,  devices.ControlChannel),
                        0x000E: ("Monitoring settings bottom",   0x013F,       1,     4,  devices.MonitoringChannel),
                        0x0012: ("Header settings carrier",      0x0140,       1,     1,  devices.HeaderInfo),
                        0x0013: ("Control settings carrier",     0x0141,      14,     4,  devices.ControlChannel),
                        0x004B: ("Monitoring settings carrier",  0x0142,      19,     4,  devices.MonitoringChannel),
                        0x0097: ("Header settings plugin",       0x0143,       1,     1,  devices.HeaderInfo),
                        0x0098: ("Control settings plugin",      0x0144,       1,     4,  devices.ControlChannel),
                        0x009C: ("Monitoring settings plugin",   0x0145,       1,     4,  devices.MonitoringChannel),
                        
                        0x00F8: ("Command",                        None,       1,     3,  devices.Command),
                        0x0139: ("Read Echo Word",               0x0151,       1,     1,  devices.EchoWord),
                        }
"""Look-up table of UART addresses and the corresponding details

        The key is the UART write address and each item is a tuple of:
    
        * description
        * UART read_addr
        * Number of entries
        * Words per entry
        * Corresponding implementation of the :class:`percival.carrier.devices.IDeviceSettings` interface
"""


class UARTRegister(object):
    ''' Represent a specific UART register on the Percival Carrier Board
    '''
    UART_ADDR_WIDTH = 16
    UART_WORD_WIDTH = 32

    def __init__(self, start_addr):
        '''Constructor
        
            :param start_addr: UART start address which also functions as a look-up key to the functionality of that register
            :type  start_addr: int
        '''
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        (self._name, self._readback_addr, self._entries, self._words_per_entry, DeviceClass) = CarrierUARTRegisters[start_addr]
        
        self.fields = None # A devices.DeviceSettings object
        if DeviceClass:
            self.fields = DeviceClass()

        if start_addr.bit_length() > self.UART_ADDR_WIDTH:
            raise ValueError("start_addr value 0x%H is greater than 16 bits"%start_addr)
        self._start_addr = start_addr
        if self._readback_addr:
            if self._readback_addr.bit_length() > self.UART_ADDR_WIDTH:
                raise ValueError("readback_addr value 0x%H is greater than 16 bits"%self._readback_addr)

    def initialize_map(self, map_words):
        self.fields.parse_map(map_words)
       
    def get_read_cmdmsg(self):
        """Generate a message to do a readback (shortcut) command of the current register map
        
            :returns: A read UART command message
            :rtype:  list of :class:`percival.carrier.txrx.TxMessage` objects
        """
        if not  self._readback_addr:
            raise TypeError("A readback shortcut is not available for \'%s\'"%self._name)
        read_cmdmsg = encoding.encode_message(self._readback_addr, 0x00000000)
        self.log.debug(read_cmdmsg)
        return txrx.TxMessage(read_cmdmsg, self._words_per_entry * self._entries)
    
    def get_write_cmdmsg(self, eom=False, device_index=0):
        """Flatten the 2D matrix of datawords into one continuous list
        
            :returns: A write UART command message
            :rtype:  list of :class:`percival.carrier.txrx.TxMessage` objects"""
        data_words = self.fields.generate_map()
        write_cmdmsg = encoding.encode_multi_message(self._start_addr + device_index, data_words)
        write_cmdmsg = [txrx.TxMessage(msg, num_response_msg=1, expect_eom=eom) for msg in write_cmdmsg]
        return write_cmdmsg
    
    
    
    