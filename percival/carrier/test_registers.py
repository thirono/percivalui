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
        self.command_reg = registers.UARTRegister( 0x0170 ) # Command Register
        cl = ".".join([__name__,str( self.__class__)])
        self.log = logging.getLogger(cl)

    def test_invalid_command_readback_msg(self):
        '''Check that a Readback message from get_read_cmdmsg() throws an exception as Command has no readback shortcut'''
        with self.assertRaises( TypeError) as cm: self.command_reg.get_read_cmdmsg( )

    def test_write_msg(self):
        self.command_reg.settings.parse_map([0,0,0])
        self.assertEqual(self.command_reg.settings.device_index, 0)
        self.assertEqual(self.command_reg.settings.device_cmd, 0)
        msg = self.command_reg.get_write_cmdmsg()
        self.assertTrue(type(msg), list)
        self.assertIsInstance(msg[0], txrx.TxMessage)
        self.assertEqual(len(msg), 3)
        expected_msg = [bytes('\x01\x70\x00\x00\x00\x00', encoding='latin-1'),
                        bytes('\x01\x71\x00\x00\x00\x00', encoding='latin-1'),
                        bytes('\x01\x72\x00\x00\x00\x00', encoding='latin-1')]
        for i in range(3):
            self.assertEqual(msg[i].message, expected_msg[i], msg[i].message)
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

