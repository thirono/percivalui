'''
Created on 5 Dec 2014

@author: Ulrik Pedersen
'''
import unittest
from carrier import registers

class TestUARTRegister(unittest.TestCase):


    def setUp(self):
        self.reg = registers.UARTRegister("TEST_REG", 0xAABB, 4, 2, 0xCCDD)

    def test_read_msg(self):
        '''Check the correctness of the generated readback command/msg from read_msg()'''
        msg = self.reg.read_msg()
        self.assertEqual(msg, '\xCC\xDD\x00\x00\x00\x00', "Readback msg not correct: %s"%str([msg]))
        
    def test_write_msg(self):
        msg = self.reg.write_msg()
        expected_msg = '\xAA\xBB\x00\x00\x00\x00' \
                       '\xAA\xBC\x00\x00\x00\x00' \
                       '\xAA\xBD\x00\x00\x00\x00' \
                       '\xAA\xBE\x00\x00\x00\x00' \
                       '\xAA\xBF\x00\x00\x00\x00' \
                       '\xAA\xC0\x00\x00\x00\x00' \
                       '\xAA\xC1\x00\x00\x00\x00' \
                       '\xAA\xC2\x00\x00\x00\x00' 
        self.assertEqual(msg, expected_msg, msg)
        
        
        
    def test_set_data_word(self):
        self.reg.set_data_word(2, 1, 0x01020304)
        expected_words = [0x00000000] * 4 * 2
        expected_words[3] = 0x01020304
        self.assertEqual(self.reg._data_words, expected_words, "Word not stored as expected")

    def test_set_data_entry(self):
        self.reg.set_data_entry(1, [0x01020304, 0x05060708, 0x09101112, 0x13141516])
        expected_words = [0x00000000] * 4 * 2
        expected_words[5] = 0x01020304
        expected_words[6] = 0x05060708
        expected_words[7] = 0x09101112
        expected_words[8] = 0x13141510
        self.assertEqual(self.reg._data_words, expected_words, "Entry of 4 words not stored as expected")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()