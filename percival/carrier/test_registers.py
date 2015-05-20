'''
Created on 5 Dec 2014

@author: Ulrik Pedersen
'''
from __future__ import unicode_literals, absolute_import
from builtins import bytes, range
import unittest, logging
from percival.carrier import registers, txrx

logging.basicConfig()
logging.getLogger(__name__).setLevel(logging.DEBUG)

class TestUARTRegister(unittest.TestCase):

    def setUp(self):
        self.command_reg = registers.UARTRegister( 0x00EC ) # Command Register
        cl = ".".join([__name__,str( self.__class__)])
        self.log = logging.getLogger(cl)

    def test_read_msg(self):
        '''Check the correctness of the generated readback command/msg from get_read_cmdmsg()'''
        msg = self.command_reg.get_read_cmdmsg()
        self.assertIsInstance(msg, txrx.TxMessage)
        self.assertEqual(msg.message, b'\x01\x44\x00\x00\x00\x00', "Readback msg not correct: %s"%str([msg]))
        
    def test_write_msg(self):
        self.command_reg.settings.parse_map([0,0,0])
        self.assertEqual(self.command_reg.settings.device_index, 0)
        self.assertEqual(self.command_reg.settings.device_cmd, 0)
        msg = self.command_reg.get_write_cmdmsg()
        self.assertTrue(type(msg), list)
        self.assertIsInstance(msg[0], txrx.TxMessage)
        self.assertEqual(len(msg), 3)
        expected_msg = [bytes('\x00\xEC\x00\x00\x00\x00', encoding='latin-1'),
                        bytes('\x00\xED\x00\x00\x00\x00', encoding='latin-1'),
                        bytes('\x00\xEE\x00\x00\x00\x00', encoding='latin-1')]
        for i in range(3):
            self.assertEqual(msg[i].message, expected_msg[i], msg[i].message)
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

