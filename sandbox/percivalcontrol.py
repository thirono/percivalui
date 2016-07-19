'''
Created on 20 May 2016

@author: Alan Greer
'''
from __future__ import print_function
from future.utils import raise_with_traceback

import argparse

from percival.log import log
from percival.control import PercivalBoard


def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--write", default="False", help="Write the initialisation configuration to the board")
    args = parser.parse_args()
    return args


def main():
    args = options()
    log.info (args)

    percival = PercivalBoard()
    if args.write == "True":
        percival.initialise_board()

    # Load channels
    percival.load_channels()

    # Startup the IpcReactor
    percival.start_reactor()


if __name__ == '__main__':
    main()
