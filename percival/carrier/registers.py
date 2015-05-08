'''
Created on 5 Dec 2014

@author: Ulrik Pedersen
'''
from __future__ import unicode_literals, absolute_import
from builtins import range
from . import encoding

import logging

       

class RegisterFunction(object):
    '''Link a register address with a certain functionality'''
    def __init__(self, description, uart_reg, reg_bank_type, board_type):
        pass
    


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
        self._start_addr = start_addr
        if start_addr.bit_length() > self.UART_ADDR_WIDTH:
            raise ValueError("start_addr value 0x%H is greater than 16 bits"%start_addr)
        self._words_per_entry = words_per_entry
        self._entries = entries
        self._readback_addr = readback_addr
        
        # Setup a container of data words
        # Ensure each entry list is an individual instance by using builtins.range()
        self._data_words = [[0x0000]*self._words_per_entry for i in range(self._entries)]
        
    def get_read_cmdmsg(self):
        read_cmdmsg = encoding.encode_message(self._readback_addr, 0x00000000)
        self.log.debug(read_cmdmsg)
        return read_cmdmsg
    
    def get_write_cmdmsg(self):
        # Flatten the 2D matrix of datawords into one continuous list
        contiguous_data_words = [word for entry in self._data_words for word in entry]
        write_cmdmsg = encoding.encode_multi_message(self._start_addr, contiguous_data_words)
        return write_cmdmsg
    
    def set_data_word(self, entry, word_index, word):
        if word.bit_length() > self.UART_WORD_WIDTH:
            raise ValueError("Word 0x%H is larger than 32 bits"%word)
        self._data_words[entry][word_index] = word
    
    def set_data_entry(self, entry, words):
        for word in words:
            if word.bit_length() > self.UART_WORD_WIDTH:
                raise ValueError("Word 0x%H is larger than 32 bits"%word)
        self._data_words[entry] = words
    
    
    