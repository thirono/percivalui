'''
Created on 5 Dec 2014

@author: Ulrik Pedersen
'''
from __future__ import unicode_literals, absolute_import
from builtins import bytes, range
import unittest, logging
from . import registers, txrx

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
        self.assertIsInstance(msg, txrx.TxMessage)
        self.assertEqual(msg.message, b'\xCC\xDD\x00\x00\x00\x00', "Readback msg not correct: %s"%str([msg]))
        
    # Disabled test: remove _ (underscore) prefix to re-enable
    def _test_write_msg(self):
        msg = self.reg.get_write_cmdmsg()
        self.assertTrue(type(msg), list)
        self.assertIsInstance(msg[0], txrx.TxMessage)
        self.assertEqual(len(msg), 4*2)
        expected_msg = [bytes('\xAA\xBB\x00\x00\x00\x00', encoding='latin-1'),
                        bytes('\xAA\xBC\x00\x00\x00\x00', encoding='latin-1'),
                        bytes('\xAA\xBD\x00\x00\x00\x00', encoding='latin-1'),
                        bytes('\xAA\xBE\x00\x00\x00\x00', encoding='latin-1'),
                        bytes('\xAA\xBF\x00\x00\x00\x00', encoding='latin-1'),
                        bytes('\xAA\xC0\x00\x00\x00\x00', encoding='latin-1'),
                        bytes('\xAA\xC1\x00\x00\x00\x00', encoding='latin-1'),
                        bytes('\xAA\xC2\x00\x00\x00\x00', encoding='latin-1')]
        for i in range(4*2):
            self.assertEqual(msg[i].message, expected_msg[i], msg[i].message)
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

