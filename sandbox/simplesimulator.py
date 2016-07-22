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
    registers = np.zeros(0x01CA, dtype=np.uint32)
    eoms = range(0x0000, 0x01B2)
    shortcuts = {0x01B3: ShortcutRegister(0x0000, 1*1),
                 0x01B4: ShortcutRegister(0x0001, 16*4),
                 0x01B5: ShortcutRegister(0x0041, 16*4),
                 0x01B6: ShortcutRegister(0x0081, 1*1),
                 0x01B7: ShortcutRegister(0x0082, 2*4),
                 0x01B8: ShortcutRegister(0x008A, 2*4),
                 0x01B9: ShortcutRegister(0x0092, 1*1),
                 0x01BA: ShortcutRegister(0x0093, 14*4),
                 0x01BB: ShortcutRegister(0x00CB, 19*4),
                 0x01BC: ShortcutRegister(0x0117, 1*1),
                 0x01BD: ShortcutRegister(0x0118, 2*4),
                 0x01BE: ShortcutRegister(0x0120, 2*4),
                 0x01BF: ShortcutRegister(0x0128, 1*32),
                 0x01C0: ShortcutRegister(0x0148, 1*8),
                 0x01C1: ShortcutRegister(0x0150, 1*8),
                 0x01C2: ShortcutRegister(0x0158, 1*8),
                 0x01C3: ShortcutRegister(0x0160, 1*16),
                 0x01C4: ShortcutRegister(0x0173, 16*1),
                 0x01C5: ShortcutRegister(0x0183, 2*1),
                 0x01C6: ShortcutRegister(0x0185, 19*1),
                 0x01C7: ShortcutRegister(0x0198, 2*1),
                 0x01C8: ShortcutRegister(0x019A, 1*8),
                 0x01C9: ShortcutRegister(0x01A2, 1*16),
                 0x01CA: ShortcutRegister(0x01B2, 1*1)}

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.settimeout(10000.0)
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

        set_value = 0
        chunk = client_sock.recv(block_read_bytes)
        while len(chunk) > 0:
            if isinstance(chunk, str):
                chunk = bytes(chunk, encoding = DATA_ENCODING)
            data = decode_message(chunk)
            for (a, w) in data:
                log.info("Message received: (0x%04X) 0x%08X", a, w)
                # Save the message to the register
                registers[a] = w
                if a in shortcuts:
                    log.info("Shortcut found: (0x%04X)", a)
                    reg, length = shortcuts[a].getshortcut()
                    msg = bytes()
                    for creg in range(reg, reg+length):
                        log.info("creg: 0x%04X   reg: (0x%08X)", creg, registers[creg])
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

                # Implementation of some expected results
                # If set value called for VCH device then the next read echo
                # is happy if it sees the same value
                if a == 0x0016 or\
                    a == 0x001A or\
                    a == 0x001E or\
                    a == 0x0022 or\
                    a == 0x0026 or\
                    a == 0x002A or\
                    a == 0x002E or\
                    a == 0x0032:
                    registers[0x0139] = w

                # Implementation of some expected results
                # If set value called for DPOT device then the next read echo
                # is happy if it sees the same value without the flag for power
                if a == 0x0036 or\
                    a == 0x003A or\
                    a == 0x003E or\
                    a == 0x0042 or\
                    a == 0x0046 or\
                    a == 0x004A:
                    registers[0x0139] = w & 0x0FFFF

            chunk = client_sock.recv(block_read_bytes)

        log.info("Client has disconnected")

if __name__ == '__main__':
    main()
