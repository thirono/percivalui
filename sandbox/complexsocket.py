'''
Created on 13 May 2015

@author: up45
'''
from __future__ import print_function
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

from percival.carrier.txrx import TxRx, TxRxContext
from percival.carrier.encoding import (encode_message, encode_multi_message, decode_message)

board_ip_address = "percival2.diamond.ac.uk"

def main():
    log.debug("complexsocket...")
    
    with TxRxContext(board_ip_address) as trx:
        
        #msg = encode_message(0x0144, 0x00000000)
        msg = encode_message(0x0144, 0x00000000)

        log.debug("as string: %s",str([msg]))
        #trx.tx_msg(msg)
        #trx.tx_msg(msg)
        #resp = trx.rx_msg()
        resp = trx.send_recv(msg)
    
    log.debug("Got %d bytes: %s", len(resp), [resp])
    
    resp = decode_message(resp)
    log.debug("Got %d words", len(resp))
    log.debug(resp)
    
if __name__ == '__main__':
    main()
    