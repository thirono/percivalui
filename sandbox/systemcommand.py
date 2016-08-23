'''
Created on 17 May 2016

@author: gnx91527
'''
from __future__ import print_function

import os
import argparse

from percival.log import log

from percival.carrier import const
from percival.carrier.txrx import TxRxContext
from percival.carrier.system import SystemCommand

board_ip_address = os.getenv("PERCIVAL_CARRIER_IP")


def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--action", action="store", default="no_operation", help="System command to send")
    args = parser.parse_args()
    return args


def main():
    args = options()
    log.info(args)

    with TxRxContext(board_ip_address) as trx:

        sys_cmd = SystemCommand(trx)
        sys_cmd.send_command(const.SystemCmd[args.action])


if __name__ == '__main__':
    main()
