'''
Created on 17 May 2016

@author: gnx91527
'''
from __future__ import print_function

import argparse
import requests
import getpass
import xlrd
from datetime import datetime

from percival.log import log
from percival.detector.spreadsheet_parser import MonitorGroupGenerator


def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--address", action="store", default="127.0.0.1:8888", help="Odin server address")
    parser.add_argument("-i", "--input", required=True, action='store', help="Input spreadsheet to parse")
    args = parser.parse_args()
    return args


def main():
    args = options()
    log.info(args)

    workbook = xlrd.open_workbook(args.input)

    mgg = MonitorGroupGenerator(workbook)
    ini_str = mgg.generate_ini()
    log.info("Sending ini: %s", ini_str)

    url = "http://" + args.address + "/api/0.1/percival/cmd_load_config"

    log.debug("Sending msg to: %s", url)
    try:
        result = requests.put(url,
                              data={
                                  'config_type': 'monitor_groups',
                                  'config': ini_str.replace('=', '::')
                              },
                              headers={
                                  'Content-Type': 'application/json',
                                  'Accept': 'application/json',
                                  'User': getpass.getuser(),
                                  'Creation-Time': str(datetime.now()),
                                  'User-Agent': 'hl_configure_monitor_groups.py'
                              }).json()
    except requests.exceptions.RequestException:
        result = {
            "error": "Exception during HTTP request, check address and Odin server instance"
        }
        log.exception(result['error'])
    return result


if __name__ == '__main__':
    main()
