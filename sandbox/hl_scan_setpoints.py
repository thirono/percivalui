'''
Created on 17 May 2016

@author: gnx91527
'''
from __future__ import print_function

import sys
import argparse
import requests
import getpass
from datetime import datetime

from percival.log import log

from percival.carrier import const
from percival.carrier.txrx import TxRxContext
from percival.carrier.system import SystemCommand
from percival.detector.detector import PercivalParameters


def options():
    desc = """Scan over set-points.  Dwell at each point.
    """
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("-a", "--address", action="store", default="127.0.0.1:8888", help="Odin server address")
    action_help = "Set-points to scan over"
    parser.add_argument("-s", "--setpoints", action="store", help=action_help)
    number_help = "Set-points to scan over"
    parser.add_argument("-n", "--number", action="store", default=10, help=number_help)
    dwell_help = "Dwell time in ms at each scan step"
    parser.add_argument("-d", "--dwell", action="store", default=1000, help=dwell_help)
    args = parser.parse_args()
    args.setpoints = [x for x in args.setpoints.split(',')]

    return args


def main():
    args = options()
    log.info(args)

    set_points = args.setpoints

    url = "http://" + args.address + "/api/0.1/percival/cmd_scan_setpoints"

    log.debug("Sending msg to: %s", url)
    try:
        result = requests.put(url,
                              data={
                                  'setpoints': set_points,
                                  'dwell': args.dwell,
                                  'steps': args.number
                              },
                              headers={
                                  'Content-Type': 'application/json',
                                  'Accept': 'application/json',
                                  'User': getpass.getuser(),
                                  'Creation-Time': str(datetime.now()),
                                  'User-Agent': 'hl_scan_setpoints.py'
                              }).json()
    except requests.exceptions.RequestException:
        result = {
            "error": "Exception during HTTP request, check address and Odin server instance"
        }
        log.exception(result['error'])

    log.info("Response: %s", result)
    return result


if __name__ == '__main__':
    main()
