'''
Created on 4 Dec 2014

@author: Ulrik Pedersen
'''

import socket

class TxRx(object):
    '''
    classdocs
    '''

    def __init__(self, fpga_addr):
        '''
        Constructor
        '''
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(1.0)
        self.sock.connect((fpga_addr, 10001))
    
    def tx_msg(self, msg):
        self.sock.sendall(msg)
    
    def rx_msg(self, expected_bytes):
        msg = ''
        while len(msg) < expected_bytes:
            chunk = self.sock.recv(expected_bytes-len(msg))
            if chunk == '':
                raise RuntimeError("socket connection broken")
            msg = msg + chunk
        return msg

    
    
    