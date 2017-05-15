"""
Created on 12 May 2016

@author: gnx91527
"""
from __future__ import print_function

import socket
import numpy as np
from threading import Thread

import signal
from builtins import bytes    # pylint: disable=W0622
from percival.carrier.encoding import DATA_ENCODING, END_OF_MESSAGE
from percival.carrier.encoding import (encode_message, decode_message)
from percival.log import log
from percival.carrier.const import *

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


class Simulator(object):
    def __init__(self):
        self.registers = np.zeros(READBACK_READ_ECHO_WORD.start_address +
                                  (READBACK_READ_ECHO_WORD.entries *
                                   READBACK_READ_ECHO_WORD.words_per_entry),
                                  dtype=np.uint32)
        self.eoms = range(0x0000, READBACK_WRITE_BUFFER.start_address)
        self.shortcuts = {READBACK_HEADER_SETTINGS_LEFT.start_address:
                              ShortcutRegister(HEADER_SETTINGS_LEFT.start_address,
                                               HEADER_SETTINGS_LEFT.entries *
                                               HEADER_SETTINGS_LEFT.words_per_entry),
                          READBACK_CONTROL_SETTINGS_LEFT.start_address:
                              ShortcutRegister(CONTROL_SETTINGS_LEFT.start_address,
                                               CONTROL_SETTINGS_LEFT.entries *
                                               CONTROL_SETTINGS_LEFT.words_per_entry),
                          READBACK_MONITORING_SETTINGS_LEFT.start_address:
                              ShortcutRegister(MONITORING_SETTINGS_LEFT.start_address,
                                               MONITORING_SETTINGS_LEFT.entries *
                                               MONITORING_SETTINGS_LEFT.words_per_entry),
                          READBACK_HEADER_SETTINGS_BOTTOM.start_address:
                              ShortcutRegister(HEADER_SETTINGS_BOTTOM.start_address,
                                               HEADER_SETTINGS_BOTTOM.entries *
                                               HEADER_SETTINGS_BOTTOM.words_per_entry),
                          READBACK_CONTROL_SETTINGS_BOTTOM.start_address:
                              ShortcutRegister(CONTROL_SETTINGS_BOTTOM.start_address,
                                               CONTROL_SETTINGS_BOTTOM.entries *
                                               CONTROL_SETTINGS_BOTTOM.words_per_entry),
                          READBACK_MONITORING_SETTINGS_BOTTOM.start_address:
                              ShortcutRegister(MONITORING_SETTINGS_BOTTOM.start_address,
                                               MONITORING_SETTINGS_BOTTOM.entries *
                                               MONITORING_SETTINGS_BOTTOM.words_per_entry),
                          READBACK_HEADER_SETTINGS_CARRIER.start_address:
                              ShortcutRegister(HEADER_SETTINGS_CARRIER.start_address,
                                               HEADER_SETTINGS_CARRIER.entries *
                                               HEADER_SETTINGS_CARRIER.words_per_entry),
                          READBACK_CONTROL_SETTINGS_CARRIER.start_address:
                              ShortcutRegister(CONTROL_SETTINGS_CARRIER.start_address,
                                               CONTROL_SETTINGS_CARRIER.entries *
                                               CONTROL_SETTINGS_CARRIER.words_per_entry),
                          READBACK_MONITORING_SETTINGS_CARRIER.start_address:
                              ShortcutRegister(MONITORING_SETTINGS_CARRIER.start_address,
                                               MONITORING_SETTINGS_CARRIER.entries *
                                               MONITORING_SETTINGS_CARRIER.words_per_entry),
                          READBACK_HEADER_SETTINGS_PLUGIN.start_address:
                              ShortcutRegister(HEADER_SETTINGS_PLUGIN.start_address,
                                               HEADER_SETTINGS_PLUGIN.entries *
                                               HEADER_SETTINGS_PLUGIN.words_per_entry),
                          READBACK_CONTROL_SETTINGS_PLUGIN.start_address:
                              ShortcutRegister(CONTROL_SETTINGS_PLUGIN.start_address,
                                               CONTROL_SETTINGS_PLUGIN.entries *
                                               CONTROL_SETTINGS_PLUGIN.words_per_entry),
                          READBACK_MONITORING_SETTINGS_PLUGIN.start_address:
                              ShortcutRegister(MONITORING_SETTINGS_PLUGIN.start_address,
                                               MONITORING_SETTINGS_PLUGIN.entries *
                                               MONITORING_SETTINGS_PLUGIN.words_per_entry),
                          READBACK_CHIP_READOUT_SETTINGS.start_address:
                              ShortcutRegister(CHIP_READOUT_SETTINGS.start_address,
                                               CHIP_READOUT_SETTINGS.entries *
                                               CHIP_READOUT_SETTINGS.words_per_entry),
                          READBACK_CLOCK_SETTINGS.start_address:
                              ShortcutRegister(CLOCK_SETTINGS.start_address,
                                               CLOCK_SETTINGS.entries *
                                               CLOCK_SETTINGS.words_per_entry),
                          READBACK_SYSTEM_SETTINGS.start_address:
                              ShortcutRegister(SYSTEM_SETTINGS.start_address,
                                               SYSTEM_SETTINGS.entries *
                                               SYSTEM_SETTINGS.words_per_entry),
                          READBACK_SAFETY_SETTINGS.start_address:
                              ShortcutRegister(SAFETY_SETTINGS.start_address,
                                               SAFETY_SETTINGS.entries *
                                               SAFETY_SETTINGS.words_per_entry),
                          READBACK_WRITE_BUFFER.start_address:
                              ShortcutRegister(WRITE_BUFFER.start_address,
                                               WRITE_BUFFER.entries *
                                               WRITE_BUFFER.words_per_entry),
                          0xFFFF: ShortcutRegister(COMMAND.start_address,
                                                   COMMAND.entries *
                                                   COMMAND.words_per_entry),  # command

                          READBACK_READ_VALUES_PERIPHERY_LEFT.start_address:
                              ShortcutRegister(READ_VALUES_PERIPHERY_LEFT.start_address,
                                               READ_VALUES_PERIPHERY_LEFT.entries *
                                               READ_VALUES_PERIPHERY_LEFT.words_per_entry),  # read left
                          READBACK_READ_VALUES_PERIPHERY_BOTTOM.start_address:
                              ShortcutRegister(READ_VALUES_PERIPHERY_BOTTOM.start_address,
                                               READ_VALUES_PERIPHERY_BOTTOM.entries *
                                               READ_VALUES_PERIPHERY_BOTTOM.words_per_entry),  # read bottom
                          READBACK_READ_VALUES_CARRIER.start_address:
                              ShortcutRegister(READ_VALUES_CARRIER.start_address,
                                               READ_VALUES_CARRIER.entries *
                                               READ_VALUES_CARRIER.words_per_entry),  # read carrier
                          READBACK_READ_VALUES_PLUGIN.start_address:
                              ShortcutRegister(READ_VALUES_PLUGIN.start_address,
                                               READ_VALUES_PLUGIN.entries *
                                               READ_VALUES_PLUGIN.words_per_entry),   # read plugin
                          READBACK_READ_VALUES_STATUS.start_address:
                              ShortcutRegister(READ_VALUES_STATUS.start_address,
                                               READ_VALUES_STATUS.entries *
                                               READ_VALUES_STATUS.words_per_entry),   # read status
                          READBACK_READ_BUFFER.start_address:
                              ShortcutRegister(READ_BUFFER.start_address,
                                               READ_BUFFER.entries *
                                               READ_BUFFER.words_per_entry),  # read buffer
                          READBACK_READ_ECHO_WORD.start_address:
                              ShortcutRegister(READ_ECHO_WORD.start_address,
                                               READ_ECHO_WORD.entries *
                                               READ_ECHO_WORD.words_per_entry)}

        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.settimeout(None)
        self.server_sock.bind(('', board_ip_port))
        self.server_sock.listen(5)

        self.thread = None

    def shutdown(self):
        """Wait a few moments for the thread to shutdown before killing it and closing the TCP socket"""
        if self.thread is not None:
            log.debug("Waiting for sim thread to complete")
            self.thread.join(2.0)
        log.debug("Closing socket")
#        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("localhost", board_ip_port))
        self.server_sock.close()
        self.thread.join(2.0)
        if self.thread.isAlive():
            log.warning("Simulation thread is still running. This should not happen")

    def start(self, forever=False, blocking=False):
        if forever and blocking:
            self._serve_forever()
        elif forever and not blocking:
            log.debug("creating thread forever")
            self.thread = Thread(target=self._serve_forever)
        elif not forever and blocking:
            self._serve()
        elif not forever and not blocking:
            log.debug("creating thread to run once")
            self.thread = Thread(target=self._serve)
        if self.thread is not None:
            log.debug("starting thread")
            self.thread.daemon = True
            self.thread.start()

    def _serve_forever(self):
        while 1:
            self._serve()

    def _serve(self):
        """Serve a TCP socket, simulating a Percival Carrier board

        The address space is empty on startup just like the Carrier.
        The function return when the client disconnects.
        """
        log.info("Listening for connections...")
        # Accept connections
        (client_sock, address) = self.server_sock.accept()
        log.info("Client connected: %s", str(address))

        msg = bytes()
        block_read_bytes = 6
        # expected_resp_len = 6

        # set_value = 0
        chunk = client_sock.recv(block_read_bytes)
        log.info("Here!")
        while len(chunk) > 0:
            if isinstance(chunk, str):
                chunk = bytes(chunk, encoding=DATA_ENCODING)
            data = decode_message(chunk)
            for (a, w) in data:
                log.info("Message received: (0x%04X) 0x%08X", a, w)
                # Save the message to the register
                self.registers[a] = w
                if a in self.shortcuts:
                    log.info("Shortcut found: (0x%04X)", a)
                    reg, length = self.shortcuts[a].getshortcut()
                    msg = bytes()
                    for creg in range(reg, reg+length):
                        log.debug("creg: 0x%04X   reg: (0x%08X)", creg, self.registers[creg])
                        msg = msg + encode_message(creg, self.registers[creg])
                    log.debug("Message length of reply: %d", len(msg))
                    client_sock.send(msg)
                else:
                    if a in self.eoms:
                        log.info("EOM required")
                        # We need to send FFFFABBABAC1 as an end of message
                        client_sock.send(END_OF_MESSAGE)
                    else:
                        # Simply send back the registers
                        client_sock.send(encode_message(a, self.registers[a]))

                # Implementation of some expected results
                # If set value called for VCH device then the next read echo
                # is happy if it sees the same value
                if a == 0x001A or\
                    a == 0x0232 or\
                    a == 0x0236 or\
                    a == 0x023A or\
                    a == 0x023E or\
                    a == 0x0242 or\
                    a == 0x0246 or\
                    a == 0x0250:
                    log.debug("***** SETTING VALUE: 0x%04X", a)
                    self.registers[READ_ECHO_WORD.start_address] = w

                # Implementation of some expected results
                # If set value called for DPOT device then the next read echo
                # is happy if it sees the same value without the flag for power
                if a == 0x0254 or\
                    a == 0x0258 or\
                    a == 0x025C or\
                    a == 0x0260 or\
                    a == 0x0264 or\
                    a == 0x0268:
                    self.registers[READ_ECHO_WORD.start_address] = w & 0x0FFFF

            chunk = client_sock.recv(block_read_bytes)

        log.info("Client has disconnected")


def main():
    sim = Simulator()
    sim.start(forever=True, blocking=True)
    #sim.shutdown()
    log.debug("Sim out!")

if __name__ == '__main__':
    main()
