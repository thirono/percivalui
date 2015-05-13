'''
Created on 13 May 2015

@author: Ulrik Pedersen
'''

from __future__ import print_function
from builtins import range
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

from percival.carrier.txrx import TxRx, TxRxContext
from percival.carrier.encoding import (encode_message, encode_multi_message, decode_message)

board_ip_address = "percival2.diamond.ac.uk"
scanrange = [(0x0144, 6),
             (0x0145, 96),
             (0x0146, None),
             ] # Currently no other "shortcut" addresses return a response

def main():
    log.debug("Scanning shortcuts...")
    
    with TxRxContext(board_ip_address) as trx:
        trx.timeout = 1.0
        #scanrange = range(0x0144, 0x0147, 1)
        for addr, expected_bytes in scanrange:
            msg = encode_message(addr, 0x00000000)
    
            log.debug("address: %X", addr)
            try:
                resp = trx.send_recv(msg, expected_bytes)
            except:
                log.debug("no response")
                continue
            data = decode_message(resp)
            log.debug(" bytes: %d  words: %d", len(resp), len(data))

if __name__ == '__main__':
    main()
    