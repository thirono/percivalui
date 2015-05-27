'''
Created on 5 Dec 2014

@author: Ulrik Pedersen
'''
from __future__ import unicode_literals, absolute_import
from builtins import range
from . import encoding

import logging

from percival.carrier import devices, txrx

BoardTypes = ["left",
              "bottom",
              "carrier",
              "plugin"]

RegisterMapTypes = {"header":     devices.HeaderInfo,
                    "control":    devices.ControlChannel,
                    "monitoring": devices.MonitoringChannel,
                    "command":    devices.Command}

# Each entry is a tuple of:     (description,                 read_addr, entries, words, DeviceSettings subclass)
CarrierUARTRegisters = {0x0000: ("Header settings left",         0x012E,       1,     1,  devices.HeaderInfo),
                        0x0001: ("Control settings left",        0x012F,       1,     1,  devices.ControlChannel),
                        0x0041: ("Monitoring settings left",     0x0130,       1,     1,  devices.MonitoringChannel),
                        0x0081: ("Header settings bottom",       0x0131,       1,     1,  devices.HeaderInfo),
                        0x0082: ("Control settings bottom",      0x0132,       1,     1,  devices.ControlChannel),
                        0x008A: ("Monitoring settings bottom",   0x0133,       1,     1,  devices.MonitoringChannel),
                        0x0092: ("Header settings carrier",      0x0134,       1,     1,  devices.HeaderInfo),
                        0x0093: ("Control settings carrier",     0x0135,       1,     1,  devices.ControlChannel),
                        0x009B: ("Monitoring settings carrier",  0x0136,       1,     1,  devices.MonitoringChannel),
                        0x00A3: ("Header settings plugin",       0x0137,       1,     1,  devices.HeaderInfo),
                        0x00A4: ("Control settings plugin",      0x0138,       1,     1,  devices.ControlChannel),
                        0x00AC: ("Monitoring settings plugin",   0x0139,       1,     1,  devices.MonitoringChannel),
                        
                        0x00EC: ("Command",                      0x0144,       1,     1,  devices.Command),
                        
                        #0x0001: ("Header settings left",        1,     1,                    None),
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
        
        self.settings = None # A devices.DeviceSettings object
        if DeviceClass:
            self.settings = devices.Command()

        if start_addr.bit_length() > self.UART_ADDR_WIDTH:
            raise ValueError("start_addr value 0x%H is greater than 16 bits"%start_addr)
        self._start_addr = start_addr
        if self._readback_addr.bit_length() > self.UART_ADDR_WIDTH:
            raise ValueError("readback_addr value 0x%H is greater than 16 bits"%self._readback_addr)
        
       
    def get_read_cmdmsg(self):
        """Generate a message to do a readback (shortcut) command of the current register map
        
            :returns: A read UART command message
            :rtype:  list of :class:`percival.carrier.txrx.TxMessage` objects
        """
        read_cmdmsg = encoding.encode_message(self._readback_addr, 0x00000000)
        self.log.debug(read_cmdmsg)
        return txrx.TxMessage(read_cmdmsg, self._words_per_entry * self._entries)
    
    def get_write_cmdmsg(self):
        """Flatten the 2D matrix of datawords into one continuous list
        
            :returns: A write UART command message
            :rtype:  list of :class:`percival.carrier.txrx.TxMessage` objects"""
        data_words = self.settings.generate_map()
        write_cmdmsg = encoding.encode_multi_message(self._start_addr, data_words)
        write_cmdmsg = [txrx.TxMessage(msg, 1) for msg in write_cmdmsg]
        return write_cmdmsg
    
    
    
    