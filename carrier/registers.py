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
        # Ensure it's a deep copy by [:]
        self._data_words = [[0x0000]*self._words_per_entry for i in xrange(self._entries)]
        
    def get_read_cmdmsg(self):
        pass
    
    def get_write_cmdmsg(self):
        pass
    
    def set_data_word(self, entry, word_index, word):
        if word.bit_length() > 32:
            raise ValueError("Word 0x%H is larger than 32 bits"%word)
        self._data_words[entry][word_index] = word
    
    def set_data_entry(self, entry, words):
        for word in words:
            if word.bit_length() > 32:
                raise ValueError("Word 0x%H is larger than 32 bits"%word)
        self._data_words[entry] = words
    
    
    