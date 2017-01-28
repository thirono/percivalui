"""
Created on 12 May 2016

@author: gnx91527
"""
from __future__ import print_function

import socket
import numpy as np

from builtins import bytes    # pylint: disable=W0622
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
    registers = np.zeros(0x0407, dtype=np.uint32)
    eoms = range(0x0000, 0x03FF)
    shortcuts = {0x03EF: ShortcutRegister(0x0000, 1 * 1),
                 0x03F0: ShortcutRegister(0x0001, 1 * 4),
                 0x03F1: ShortcutRegister(0x0005, 1 * 4),
                 0x03F2: ShortcutRegister(0x0009, 1 * 1),
                 0x03F3: ShortcutRegister(0x000A, 52 * 4),
                 0x03F4: ShortcutRegister(0x00DA, 84 * 4),
                 0x03F5: ShortcutRegister(0x022A, 1 * 1),
                 0x03F6: ShortcutRegister(0x022B, 14 * 4),
                 0x03F7: ShortcutRegister(0x0263, 19 * 4),
                 0x03F8: ShortcutRegister(0x02AF, 1 * 1),
                 0x03F9: ShortcutRegister(0x02B0, 1 * 4),
                 0x03FA: ShortcutRegister(0x02B4, 1 * 4),
                 0x03FB: ShortcutRegister(0x02B8, 1 * 32),
                 0x03FC: ShortcutRegister(0x02D8, 1 * 8),
                 0x03FD: ShortcutRegister(0x02E0, 1 * 18),
                 0x03FE: ShortcutRegister(0x02F2, 1 * 8),
                 0x03FF: ShortcutRegister(0x02FA, 1 * 64),
                 0x0000: ShortcutRegister(0x033A, 1 * 3),  # command

                 0x0400: ShortcutRegister(0x033D, 1 * 1),  # read left
                 0x0401: ShortcutRegister(0x033E, 84 * 1),  # read bottom
                 0x0402: ShortcutRegister(0x0392, 19 * 1),  # read carrier
                 0x0403: ShortcutRegister(0x03A5, 1 * 1),   # read plugin
                 0x0404: ShortcutRegister(0x03A6, 1 * 8),   # read status
                 0x0405: ShortcutRegister(0x03AE, 1 * 64),  # read buffer
                 0x0406: ShortcutRegister(0x03EE, 1 * 1)}


    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.settimeout(None)
    server_sock.bind(('', board_ip_port))
    server_sock.listen(5)

    while 1:
        log.info("Listening for connections...")
        # Accept connections
        (client_sock, address) = server_sock.accept()
        log.info("Client connected: %s", str(address))

        msg = bytes()
        block_read_bytes = 6
        # expected_resp_len = 6

        # set_value = 0
        chunk = client_sock.recv(block_read_bytes)
        while len(chunk) > 0:
            if isinstance(chunk, str):
                chunk = bytes(chunk, encoding=DATA_ENCODING)
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
                        log.debug("EOM required")
                        # We need to send FFFFABBABAC1 as an end of message
                        client_sock.send(END_OF_MESSAGE)
                    else:
                        # Simply send back the registers
                        client_sock.send(encode_message(a, registers[a]))

                # Implementation of some expected results
                # If set value called for VCH device then the next read echo
                # is happy if it sees the same value
                if a == 0x022E or\
                    a == 0x0232 or\
                    a == 0x0236 or\
                    a == 0x023A or\
                    a == 0x023E or\
                    a == 0x0242 or\
                    a == 0x0246 or\
                    a == 0x0250:
                    registers[0x03EE] = w

                # Implementation of some expected results
                # If set value called for DPOT device then the next read echo
                # is happy if it sees the same value without the flag for power
                if a == 0x0254 or\
                    a == 0x0258 or\
                    a == 0x025C or\
                    a == 0x0260 or\
                    a == 0x0264 or\
                    a == 0x0268:
                    registers[0x03EE] = w & 0x0FFFF

            chunk = client_sock.recv(block_read_bytes)

        log.info("Client has disconnected")

if __name__ == '__main__':
    main()
