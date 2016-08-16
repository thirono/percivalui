'''
Created on 20 May 2016

@author: Alan Greer
'''
from __future__ import print_function

import os
import argparse

from percival.log import log
from percival.detector.ipc_channel import IpcChannel
from percival.detector.ipc_message import IpcMessage

board_ip_address = os.getenv("PERCIVAL_CARRIER_IP")


def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--write", default="False", help="Write the initialisation configuration to the board")
#    parser.add_argument("-o", "--output", action='store', help="Output HDF5 filename")
#    parser.add_argument("-p", "--period", action='store', type=float, default=1.0, help="Control the loop period time")
#    parser.add_argument("channel", action='store', help="Control Channel to scan")
    args = parser.parse_args()
    return args


def main():
    args = options()
    log.info(args)

    log.debug("Message")
    msg = IpcMessage(IpcMessage.MSG_TYPE_CMD, IpcMessage.MSG_VAL_CMD_CONFIGURE)
#    msg.set_param("status_loop", "run")
    msg.set_param("status_loop", "stop")
    channel = IpcChannel(IpcChannel.CHANNEL_TYPE_PAIR)
    channel.connect("tcp://127.0.0.1:8888")
    #time.sleep(1.0)
    channel.send(msg.encode())


if __name__ == '__main__':
    main()
