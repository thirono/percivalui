'''
Created on 17 May 2016

@author: gnx91527
'''
from __future__ import print_function

import argparse

from percival.log import log
from percival.scripts.util import PercivalClient


def options():
    desc = """Download the channel settings from the ini file to the hardware
    """
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("-a", "--address", action="store", default="127.0.0.1:8888",
                        help="Odin server address (default 127.0.0.1:8888)")
    wait_help = "Wait for the command to complete (default true)"
    parser.add_argument("-w", "--wait", action="store", default="true", help=wait_help)
    args = parser.parse_args()
    return args


def main():
    return_value = 0
    args = options()
    log.info(args)

    pc = PercivalClient(args.address)
    result = pc.send_command('cmd_download_channel_cfg', 'hl_download_channel_settings.py')
    log.info("Response: %s", result)
    if args.wait.lower() == "true":
        result = pc.wait_for_command_completion(0.2)

    if result['response'] == 'Failed':
        return_value = -1

    return return_value


if __name__ == '__main__':
    main()
