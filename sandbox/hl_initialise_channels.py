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
    desc = """Send the initialise command to channels that support it
    """
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("-a", "--address", action="store", default="127.0.0.1:8888", help="Odin server address")
    args = parser.parse_args()
    return args


def main():
    args = options()
    log.info(args)

    url = "http://" + args.address + "/api/0.1/percival/cmd_initialise_channels"

    log.debug("Sending msg to: %s", url)
    try:
        result = requests.put(url,
                              headers={
                                  'Content-Type': 'application/json',
                                  'Accept': 'application/json',
                                  'User': getpass.getuser(),
                                  'Creation-Time': str(datetime.now()),
                                  'User-Agent': 'hl_initialise_channels.py'
                              }).json()
    except requests.exceptions.RequestException:
        result = {
            "error": "Exception during HTTP request, check address and Odin server instance"
        }
        log.exception(result['error'])
    return result


if __name__ == '__main__':
    main()
