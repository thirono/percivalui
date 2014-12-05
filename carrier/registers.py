'''
Created on 5 Dec 2014

@author: Ulrik Pedersen
'''

UART_ADDR_WIDTH = 16
UART_WORD_WIDTH = 32

class UARTRegister(object):
    '''
    classdocs
    '''

    def __init__(self, name, start_addr, words_per_entry, entries, readback_addr):
        '''
        Constructor
        '''
        self._name = name
        self._start_addr = start_addr
        self._words_per_entry = words_per_entry
        self._entries = entries
        self._readback_addr = readback_addr
        
        # Setup a container of data words
        self._data_words = [0x0000] * self._entries * self._words_per_entry
        
    def get_read_cmdmsg(self):
        pass
    
    def get_write_cmdmsg(self):
        pass
    
    def set_data_word(self, entry, word_index, word):
        pass
    
    def set_data_entry(self, entry, words):
        pass
    
    def _data_index(self, entry, word_index):
        return entry * self._words_per_entry + word_index
    
    