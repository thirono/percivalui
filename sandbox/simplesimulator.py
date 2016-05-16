'''
Created on 12 May 2016

@author: gnx91527
'''
from __future__ import print_function

import socket
import numpy as np

from builtins import bytes
from percival.carrier.encoding import DATA_ENCODING, END_OF_MESSAGE
from percival.carrier.encoding import (encode_message, decode_message)
from percival.log import log

board_ip_port = 10001


def bytes_to_str(byte_list):
    return "".join([chr(b) for b in byte_list])


class ShortcutRegister(object):
    """
    Contains the register start address and number of words to return
    when this register is written to
    """
    def __init__(self, register, length):
        self.register = register
        self.length = length

    def getshortcut(self):
        return self.register, self.length


def main():
    registers = np.zeros(0x0152, dtype=np.int32)
    eoms = [0x0016, 0x00F8]
    shortcuts = {0x0141: ShortcutRegister(0x0013, 14*4),
                 0x014D: ShortcutRegister(0x00FD, 19*1)}

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.settimeout(128.0)
    server_sock.bind(('', board_ip_port))
    server_sock.listen(5)

    while 1:
        log.info("Listening for connections...")
        # Accept connections
        (client_sock, address) = server_sock.accept()
        log.info("Client connected: %s", str(address))

        msg = bytes()
        block_read_bytes = 6
        expected_resp_len = 6

        chunk = client_sock.recv(block_read_bytes)
        while len(chunk) > 0:
            chunk = bytes(chunk, encoding=DATA_ENCODING)
            data = decode_message(chunk)
            for (a, w) in data:
                log.info("Message received: (0x%04X) 0x%08X", a, w)
                if shortcuts.has_key(a):
                    log.info("Shortcut found: (0x%04X)", a)
                    reg, length = shortcuts[a].getshortcut()
                    msg = bytes()
                    for creg in range(reg, reg+length):
                        msg = msg + encode_message(creg, registers[creg])
                    log.info("Message length of reply: %d", len(msg))
                    client_sock.send(msg)
                else:
                    if a in eoms:
                        # We need to send FFFFABBABAC1 as an end of message
                        client_sock.send(END_OF_MESSAGE)
                    else:
                        # Simply send back the registers
                        client_sock.send(encode_message(a, registers[a]))



            chunk = client_sock.recv(block_read_bytes)

        log.info("Client has disconnected")

if __name__ == '__main__':
    main()
