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

# Look-up table of addresses and the corresponding details:
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
                        
                        0x00EC: ("Command",                        None,       1,     1,  devices.Command),
                        
                        #0x0001: ("Header settings left",        1,     1,                    None),
                        }


class UARTRegister(object):
    '''
    classdocs
    '''
    UART_ADDR_WIDTH = 16
    UART_WORD_WIDTH = 32

    def __init__(self, name, start_addr, words_per_entry, entries, readback_addr):
        '''
        Constructor
        '''
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self._name = name
        self._words_per_entry = words_per_entry
        self._entries = entries
        self.settings = None # A devices.DeviceSettings object

        if start_addr.bit_length() > self.UART_ADDR_WIDTH:
            raise ValueError("start_addr value 0x%H is greater than 16 bits"%start_addr)
        self._start_addr = start_addr
        if readback_addr.bit_length() > self.UART_ADDR_WIDTH:
            raise ValueError("readback_addr value 0x%H is greater than 16 bits"%readback_addr)
        self._readback_addr = readback_addr
        
       
    def get_read_cmdmsg(self):
        """Generate a message to do a readback (shortcut) command of the current register map
        
        :returns: A TxMessage object which contain the actual message as well as the number of
                  words to expect in response
        """
        read_cmdmsg = encoding.encode_message(self._readback_addr, 0x00000000)
        self.log.debug(read_cmdmsg)
        return txrx.TxMessage(read_cmdmsg, self._words_per_entry * self._entries)
    
    def get_write_cmdmsg(self):
        # Flatten the 2D matrix of datawords into one continuous list
        data_words = self.settings.generate_map()
        write_cmdmsg = encoding.encode_multi_message(self._start_addr, data_words)
        write_cmdmsg = [txrx.TxMessage(msg, 1) for msg in write_cmdmsg]
        return write_cmdmsg
    
    
    
    