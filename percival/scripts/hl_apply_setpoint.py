'''
Created on 17 May 2016

@author: gnx91527
'''
from __future__ import print_function

import argparse

from percival.log import log
from percival.scripts.util import PercivalClient


def options():
    desc = """Apply a set-point to the Percival Carrier Board
    """
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("-a", "--address", action="store", default="127.0.0.1:8888",
                        help="Odin server address (default 127.0.0.1:8888)")
    action_help = "Set-point to apply"
    parser.add_argument("-s", "--setpoint", action="store", help=action_help)
    args = parser.parse_args()
    return args


def main():
    args = options()
    log.info(args)

    set_point = args.setpoint

    pc = PercivalClient(args.address)
    pc.apply_setpoint(set_point, 'hl_apply_setpoint.py')


if __name__ == '__main__':
    main()
