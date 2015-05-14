'''
Created on 5 Dec 2014

@author: Ulrik Pedersen
'''
from __future__ import unicode_literals, absolute_import
from builtins import bytes, range
import unittest, logging
from . import registers

logging.basicConfig()
logging.getLogger(__name__).setLevel(logging.DEBUG)

class TestUARTRegister(unittest.TestCase):

    def setUp(self):
        self.reg = registers.UARTRegister("TEST_REG", 0xAABB, 4, 2, 0xCCDD)
        cl = ".".join([__name__,str( self.__class__)])
        self.log = logging.getLogger(cl)

    def test_read_msg(self):
        '''Check the correctness of the generated readback command/msg from get_read_cmdmsg()'''
        msg = self.reg.get_read_cmdmsg()
        self.assertEqual(msg, b'\xCC\xDD\x00\x00\x00\x00', "Readback msg not correct: %s"%str([msg]))
        
    def test_write_msg(self):
        msg = self.reg.get_write_cmdmsg()
        expected_msg = [bytes('\xAA\xBB\x00\x00\x00\x00', encoding='latin-1'),
                        bytes('\xAA\xBC\x00\x00\x00\x00', encoding='latin-1'),
                        bytes('\xAA\xBD\x00\x00\x00\x00', encoding='latin-1'),
                        bytes('\xAA\xBE\x00\x00\x00\x00', encoding='latin-1'),
                        bytes('\xAA\xBF\x00\x00\x00\x00', encoding='latin-1'),
                        bytes('\xAA\xC0\x00\x00\x00\x00', encoding='latin-1'),
                        bytes('\xAA\xC1\x00\x00\x00\x00', encoding='latin-1'),
                        bytes('\xAA\xC2\x00\x00\x00\x00', encoding='latin-1')]
        self.assertEqual(msg, expected_msg, msg)
        
    def test_set_data_word(self):
        self.reg.set_data_word(1, 1, 0x01020304)
        expected_words = [[0x00000000] * 4 for i in range(2)]
        expected_words[1][1] = 0x01020304
        self.assertEqual(self.reg._data_words, expected_words, "Word not stored as expected")

    def test_set_data_word_outofrange(self):
        with self.assertRaises(ValueError):
            self.reg.set_data_word(3, 1, 0x0102030405)
            
    def test_set_data_word_outofindex(self):
        with self.assertRaises(IndexError):
            self.reg.set_data_word(4, 0, 0x01020304)
        with self.assertRaises(IndexError):
            self.reg.set_data_word(1, 77, 0x01020304)

    def test_set_data_entry(self):
        self.reg.set_data_entry(1, [0x01020304, 0x05060708, 0x09101112, 0x13141516])
        expected_words = [[0x00000000] * 4 for i in range(2)]
        expected_words[1][0] = 0x01020304
        expected_words[1][1] = 0x05060708
        expected_words[1][2] = 0x09101112
        expected_words[1][3] = 0x13141516
        self.log.debug(expected_words)
        self.assertEqual(self.reg._data_words, expected_words, "Entry of 4 words not stored as expected")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

