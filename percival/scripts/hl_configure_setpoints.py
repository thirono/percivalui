'''
Created on 17 May 2016

@author: gnx91527
'''
from __future__ import print_function

import argparse
import xlrd

from percival.log import log
from percival.scripts.util import PercivalClient
from percival.detector.spreadsheet_parser import SetpointGroupGenerator


def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--address", action="store", default="127.0.0.1:8888",
                        help="Odin server address (default 127.0.0.1:8888)")
    parser.add_argument("-i", "--input", required=True, action='store', help="Input spreadsheet to parse")
    wait_help = "Wait for the command to complete (default true)"
    parser.add_argument("-w", "--wait", action="store", default="true", help=wait_help)
    parser.add_argument("--textdump", action="store_true", help="send to stdout instead of odin")
    args = parser.parse_args()
    return args


def main():
    args = options()
    log.info(args)

    workbook = xlrd.open_workbook(args.input)

    sgg = SetpointGroupGenerator(workbook)
    ini_str = sgg.generate_ini()
    if args.textdump:
        print (ini_str);
    else:
        pc = PercivalClient(args.address)
        result = pc.send_configuration('setpoints',
                                       ini_str,
                                       'hl_configure_setpoints.py',
                                       wait=(args.wait.lower() == "true"))
        log.info("Response: %s", result)


if __name__ == '__main__':
    main()
