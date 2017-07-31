'''
Created on 17 May 2016

@author: gnx91527
'''
from __future__ import print_function

import argparse

from percival.log import log
from percival.scripts.util import PercivalClient


def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--address", action="store", default="127.0.0.1:8888",
                        help="Odin server address (default 127.0.0.1:8888)")
    parser.add_argument("-i", "--input", required=True, action='store', help="Input settings ini file to apply")
    args = parser.parse_args()
    return args


def main():
    args = options()
    log.info(args)

    with open(args.input, 'r') as ini_file:
        ini_str = ini_file.read()

    pc = PercivalClient(args.address)
    pc.send_configuration('sensor_debug', ini_str, 'hl_configure_sensor_debug.py')


if __name__ == '__main__':
    main()
