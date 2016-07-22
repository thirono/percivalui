'''
Created on 20 May 2016

@author: Alan Greer
'''
from __future__ import print_function
from future.utils import raise_with_traceback

import argparse

from percival.log import log

import os
from percival.carrier.encoding import (encode_message, decode_message)

from percival.carrier import const
from percival.carrier.settings import BoardSettings
from percival.carrier.txrx import TxRxContext
from percival.control import PercivalParameters

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
        percival_params = PercivalParameters()
        percival_params.load_ini()

        bs = BoardSettings(trx, const.BoardTypes.left)
        cmd_msg = bs.initialise_board(percival_params)
        bs = BoardSettings(trx, const.BoardTypes.bottom)
        cmd_msg += bs.initialise_board(percival_params)
        bs = BoardSettings(trx, const.BoardTypes.carrier)
        cmd_msg += bs.initialise_board(percival_params)
        bs = BoardSettings(trx, const.BoardTypes.plugin)
        cmd_msg += bs.initialise_board(percival_params)

        # We've been asked to download the settings to the board
        if args.write.upper() == "TRUE":
            for msg in cmd_msg:
                try:
                    trx.send_recv_message(msg)
                except:
                    log.warning("no response (message: %s", cmd_msg)

        ## Now read back and check we are matching
        scanrange = range(0x01B3, 0x01BE + 1, 1)
        expected_bytes = None
        for addr in scanrange:
            msg = encode_message(addr, 0x00000000)

            try:
                resp = trx.send_recv(msg, expected_bytes)
            except:
                log.warning("no response (addr: %X", addr)
                continue
            data = decode_message(resp)
            for (a, w) in data:
                test_data = decode_message(cmd_msg[a].message)
                ta, tw = test_data[0]
                if w == tw:
                    log.info("Match address 0X%04X [0X%08X] == [0X%08X]", a, w, tw)
                else:
                    log.info("Mismatch!!")

if __name__ == '__main__':
    main()