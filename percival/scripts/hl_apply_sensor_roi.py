'''
Created on 17 May 2016

@author: gnx91527
'''
from __future__ import print_function

import argparse

from percival.log import log
from percival.scripts.util import PercivalClient


def options():
    desc = """Send the apply sensor ROI command to the Percival Carrier Board
    """
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("-a", "--address", action="store", default="127.0.0.1:8888",
                        help="Odin server address (default 127.0.0.1:8888)")
    args = parser.parse_args()
    return args


def main():
    args = options()
    log.info(args)

    pc = PercivalClient(args.address)
    pc.send_command('cmd_apply_roi', 'hl_apply_sensor_roi.py')


if __name__ == '__main__':
    main()
