'''
Created on 17 May 2016

@author: gnx91527
'''
from __future__ import print_function

import os
import argparse

from percival.log import log

from percival.carrier import const
from percival.carrier.registers import UARTRegister
from percival.carrier.txrx import TxRxContext

board_ip_address = os.getenv("PERCIVAL_CARRIER_IP")

def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--action", default="no_operation", help="System command to send")
    args = parser.parse_args()
    return args


def main():
    args = options()
    log.info (args)

    with TxRxContext(board_ip_address) as trx:
        reg_command = UARTRegister(const.COMMAND)
        reg_command.initialize_map([0,0,0])

        log.debug("Sending command: %s", const.SystemCmd.no_operation)
        reg_command.fields.system_cmd = const.SystemCmd.no_operation.value
        cmd_msg = reg_command.get_write_cmd_msg(True)[2]
        response = trx.send_recv_message(cmd_msg)
        # Log the message response
        log.debug("Response: %s", response)

        log.debug("Sending command: %s", const.SystemCmd[args.action])
        reg_command.fields.system_cmd = const.SystemCmd[args.action].value
        cmd_msg = reg_command.get_write_cmd_msg(True)[2]
        response = trx.send_recv_message(cmd_msg)
        # Log the message response
        log.debug("Response: %s", response)


if __name__ == '__main__':
    main()
