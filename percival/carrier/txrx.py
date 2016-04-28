"""
Communications module for the Percival Carrier Board XPort interface.
"""
from __future__ import unicode_literals, absolute_import
from builtins import bytes

import logging
import binascii
import socket
from contextlib import contextmanager 

from percival.carrier.encoding import DATA_ENCODING, NUM_BYTES_PER_MSG, END_OF_MESSAGE
from percival.carrier.encoding import (encode_message, encode_multi_message, decode_message)


def hexify(registers):
    """
    Utility function to generate a string representation of a register map with hexadecimal formatted values.

    :param registers: A list of ints or tuples that represents an register map
    :type registers:  list
    :return: string
    """
    registers_str = "|"
    if type(registers[0]) == int:
        for word in registers:
            registers_str += " %s |"%(hex(word))
    elif type(registers[0]) == tuple:
        for addr,word in registers:
            registers_str += " %s: %s |"%(hex(addr), hex(word))
    else:
        registers_str = str(registers)
    return registers_str


class TxMessage(object):
    """Encapsulate a single Percival carrier board message and the number of messages to expect in response"""
    def __init__(self, message, num_response_msg=1, expect_eom=False):
        """ TxMessage constructor
        
            :param message: A Percival Carrier Board message contain address (2 bytes) and data (4 bytes)
            :type message: bytearray
            :param num_response_msg: Number of messages to expect in response
            :param num_response_msg: int
            :param expect_eom: set true if an end-of-message is expected in response
            :type expect_eom: boolean
        """
        self.num_response_msg = num_response_msg
        self._message = message
        self._expect_eom = False
        if expect_eom:
            self._expect_eom = END_OF_MESSAGE
        
    @property
    def message(self):
        return self._message
    
    @property
    def expected_bytes(self):
        return self.num_response_msg * NUM_BYTES_PER_MSG
    
    @property
    def expected_response(self):
        if self._expect_eom:
            return END_OF_MESSAGE

    def validate_eom(self, response):
        if self._expect_eom:
            return response == self._expect_eom

        # If no EOM is expected then just return OK
        else:
            return True

    def __repr__(self):
        s = "<TxMessage msg=0x%s %d bytes %s>"%(binascii.hexlify(self._message).upper(),
                                                               self.num_response_msg, bool(self._expect_eom))
        return s
        
    def __str__(self, *args, **kwargs):
        s = "<TxMessage msg=0x%s exp. resp.: %d bytes EOM: %s>"%(binascii.hexlify(self._message).upper(),
                                                               self.num_response_msg, bool(self._expect_eom))
        return s

class TxRx(object):
    """
    Transmit and receive data and commands to/from the Carrier Board through the XPort Ethernet
    """

    def __init__(self, fpga_addr, port = 10001, timeout = 2.0):
        '''TxRx Constructor
        
            :param fpga_addr: IP address or network name of the Carrier Board XPort device
            :type  fpga_addr: `str`
            :param port:      IP port number
            :type  port:      `int`
            :param timeout:   Socket communication timeout (seconds)
            :type  timeout:   `float`
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
        """Transmit a single message of :const:`percival.carrier.encoding.NUM_BYTES_PER_MSG` bytes to the Carrier Board
        
        :param msg: Message to transmit
        :type  msg: bytearray
        """
        self.sock.sendall(msg)
    
    def rx_msg(self, expected_bytes = None):
        """Receive messages of up to `expected_bytes` length
        
        :param expected_bytes: Number of bytes expected to be received. If `expected_bytes`
                               is None, read at least one single message
        :raises `RuntimeError`: if a message of 0 bytes is received indicating a broken socket connection
        :returns: The received message
        :rtype:   bytearray
        """
        msg = bytes()
        block_read_bytes = expected_bytes
        expected_resp_len = expected_bytes
        
        if expected_bytes == None: 
            expected_resp_len = NUM_BYTES_PER_MSG
            block_read_bytes = 1024
        
        while len(msg) < expected_resp_len:
            if expected_bytes:
                block_read_bytes = expected_bytes-len(msg)
            chunk = self.sock.recv(block_read_bytes)
            chunk = bytes(chunk, encoding = DATA_ENCODING)
            if len(chunk) == 0:
                raise RuntimeError("socket connection broken (expected a multiple of 6 bytes)")
            msg = msg + chunk
        return msg

    def send_recv(self, msg, expected_bytes = None):
        """Send `msg` and wait for receipt of `expected_bytes` in response or timeout
        
        :param msg: UART message to send
        :type  msg: bytearray
        :returns:   Response from UART
        :rtype:     bytearray
        """ 
        self.tx_msg(msg)
        resp = self.rx_msg(expected_bytes)
        return resp
    
    def send_recv_message(self, message):
        """Send a message and wait for response
        
        :param message: a single message to send
        :type message: :obj:`TxMessage`
        :retuns: Response from UART as a list of tuples: [(address, data)...]
        :rtype:  list
        """
        self.log.debug("Sending:   %s"%message)
        if not isinstance(message, TxMessage):
            raise TypeError("message must be of type TxMessage, not %s"%str(type(message)))
        
        self.tx_msg(message.message)
        resp = self.rx_msg(message.expected_bytes)
        result = decode_message(resp)

        self.log.debug(" response: %s"%hexify(result))
        # Check for expected response
        if not message.validate_eom(resp):
            raise RuntimeError("Expected EOM on TxMessage: %s - got %s"%(str(message), str(result)))
        return result
        
    
    def clean(self):
        """Shutdown and close the socket safely
            
        Sockets are normally closed down cleanly on exit from the interpreter, however this method
        may be used in case the socket need to be closed down temporarily.
        """
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()


@contextmanager
def TxRxContext(*args, **kwargs):
    """Provide a context which keeps a :class:`TxRx` module alive with an open socket only for the duration of the context
    
    Minimal example:

    >>> msg = encode_message(0x0144, 0x00000000) # Header Info Readback
    >>>
    >>> # Start the context - create the TxRx object and open the socket
    >>> with TxRxContext("192.168.1.3") as trx:
    >>>     response = trx.send_recv(msg)
    >>> # End of context - socket is closed down cleanly
    >>>
    >>> response = decode_message(response)
    >>> print response
    """
    trx = TxRx(*args, **kwargs)
    yield trx
    trx.clean()
    
       
            