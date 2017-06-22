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

system_commands = "\n\t".join([name for name, tmp in const.SystemCmd.__members__.items()])


def options():
    desc = """Send a System Command to the Percival Carrier Board
    """
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("-a", "--address", action="store", default="127.0.0.1:8888", help="Odin server address")
    action_help = "System command to send. Valid commands are: %s" % system_commands
    parser.add_argument("-c", "--command", action="store", default="no_operation", help=action_help)
    args = parser.parse_args()
    return args


def main():
    args = options()
    log.info(args)

    try:
        system_command = const.SystemCmd[args.command.lower()]
    except KeyError:
        log.error("Invalid command \'%s\' supplied to --command", args.command)
        print("Invalid command: \'%s\'" % args.command)
        print("Valid commands are: \n\t%s" % system_commands)
        sys.exit(-1)

    url = "http://" + args.address + "/api/0.1/percival/cmd_system_command"


    log.debug("Sending msg to: %s", url)
    try:
        result = requests.put(url,
                              data={
                                  'name': system_command.name
                              },
                              headers={
                                  'Content-Type': 'application/json',
                                  'Accept': 'application/json',
                                  'User': getpass.getuser(),
                                  'Creation-Time': str(datetime.now()),
                                  'User-Agent': 'hl_system_command.py'
                              }).json()
    except requests.exceptions.RequestException:
        result = {
            "error": "Exception during HTTP request, check address and Odin server instance"
        }
        log.exception(result['error'])
    return result

    #pcvl_params = PercivalParameters()
    #pcvl_params.load_ini()
    #log.info("Connecting to Carrier IP: %s", pcvl_params.carrier_ip)

    #with TxRxContext(pcvl_params.carrier_ip) as trx:
    #    log.debug("Connected to %s", pcvl_params.carrier_ip)
    #    print("Sending System Command: %s", system_command.name)
    #    sys_cmd = SystemCommand(trx)
    #    sys_cmd.send_command(system_command)


if __name__ == '__main__':
    main()
