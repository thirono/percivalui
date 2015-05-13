'''
Created on 4 Dec 2014

@author: Ulrik Pedersen
'''
from __future__ import unicode_literals, absolute_import
from builtins import bytes

import logging

import socket
from contextlib import contextmanager 

from percival.carrier.encoding import DATA_ENCODING

class TxRx(object):
    '''
    Transmit and receive data and commands to/from the Carrier Board through the XPort Ethernet
    '''

    def __init__(self, fpga_addr, port = 10001, timeout = 2.0):
        '''
        Constructor
        '''
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        
        self._fpga_addr = (fpga_addr, port)
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(timeout)
        self.log.debug("connecting to FPGA: %s", str(self._fpga_addr))
        self.sock.connect(self._fpga_addr)
    
    @property
    def fpga_addr(self):
        return self._fpga_addr
    
    @property
    def timeout(self):
        return self.sock.gettimeout()
    @timeout.setter
    def timeout(self, value):
        self.sock.settimeout(value)
    
    def tx_msg(self, msg):
        self.sock.sendall(msg)
    
    def rx_msg(self, expected_bytes = None):
        msg = bytes()
        block_read_bytes = expected_bytes
        expected_resp_len = expected_bytes
        
        if expected_bytes == None: 
            expected_resp_len = 1
            block_read_bytes = 1024
        
        while len(msg) < expected_resp_len:
            if expected_bytes:
                block_read_bytes = expected_bytes-len(msg)
            chunk = self.sock.recv(block_read_bytes)
            chunk = bytes(chunk, encoding = DATA_ENCODING)
            if len(chunk) == 0:
                raise RuntimeError("socket connection broken")
            msg = msg + chunk
        return msg

    def send_recv(self, msg, expected_bytes = None):
        self.tx_msg(msg)
        resp = self.rx_msg(expected_bytes)
        return resp
    
    def clean(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        
@contextmanager
def TxRxContext(*args, **kwargs):
    trx = TxRx(*args, **kwargs)
    yield trx
    trx.clean()
    
       
            