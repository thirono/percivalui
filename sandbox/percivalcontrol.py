'''
Created on 20 May 2016

@author: Alan Greer
'''
from __future__ import print_function
from future.utils import raise_with_traceback

import os, time
import argparse

import logging
from percival.log import log

import os
from percival.carrier.txrx import TxRxContext
from percival.control import PercivalBoard

from percival.detector.ipc_channel import IpcChannel
from percival.detector.ipc_message import IpcMessage
from percival.detector.ipc_reactor import IpcReactor

board_ip_address = os.getenv("PERCIVAL_CARRIER_IP")


def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--write", default="False", help="Write the initialisation configuration to the board")
    args = parser.parse_args()
    return args


def main():
    args = options()
    log.info (args)

    with TxRxContext(board_ip_address) as trx:

        percival = PercivalBoard(trx)
        if args.write == "True":
            percival.initialise_board()

        # Turn on global monitoring
        percival.set_global_monitoring(True)

        percival.load_channels()
        percival.update("Temperature1")
        percival.update("Temperature2")
        percival.update("Temperature3")

        log.debug("Temperature 1 %.2f", percival.temperature("Temperature1"))
        log.debug("Temperature 2 %.2f", percival.temperature("Temperature2"))
        log.debug("Temperature 3 %.2f", percival.temperature("Temperature3"))

        channel = IpcChannel(IpcChannel.CHANNEL_TYPE_PAIR)
        channel.bind("tcp://127.0.0.1:8888")

        reactor = IpcReactor()
        reactor.register_channel(channel, percival.callback)
        reactor.register_timer(1000, 0, percival.timer)
        reactor.run()


if __name__ == '__main__':
    main()
