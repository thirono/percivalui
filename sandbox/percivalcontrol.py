'''
Created on 20 May 2016

@author: Alan Greer
'''
from __future__ import print_function
from future.utils import raise_with_traceback

import argparse

from percival.log import log

import os
from percival.carrier.txrx import TxRxContext
from percival.control import PercivalBoard

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

        # Load channels
        percival.load_channels()

        # Turn on global monitoring
        percival.set_global_monitoring(True)

        # Setup the status publishing channel
        percival.setup_status_channel("tcp://127.0.0.1:8889")

        # Startup the control channel and IpcReactor
        percival.setup_control_channel("tcp://127.0.0.1:8888")
        percival.start_reactor()


if __name__ == '__main__':
    main()
