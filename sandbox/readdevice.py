'''
Created on 19 May 2015

@author: up45
'''
from __future__ import print_function

import time, binascii

from percival.log import log

from percival.carrier.registers import UARTRegister
from percival.carrier.txrx import TxRx, TxRxContext, TxMessage
from percival.carrier.encoding import (encode_message, encode_multi_message, decode_message)

board_ip_address = "percival2.diamond.ac.uk"

def main():
    log.debug("read device...")
    
    with TxRxContext(board_ip_address) as trx:
    
        cmd = UARTRegister(0x00EC)  # Command register
        cmd.settings.parse_map([0,0,0]) # initialise all registers to 0
        
        # First generate and send a no-op system command
        cmd.settings.system_cmd = 0 # no-op system command
        cmd.settings.system_cmd_data = 0  # not used
        no_op_cmd_msg = cmd.get_write_cmdmsg()[2]
        log.info("System no-op command: %s", str(no_op_cmd_msg))
        response = trx.send_recv_message(no_op_cmd_msg)
        decoded_response = decode_message(response)
        log.info("    response: 0x%04X: 0x%08X", decoded_response[0][0], decoded_response[0][1])
       
        cmd.settings.system_cmd = 2 # disable global monitoring
        disable_global_mon_cmd_msg = cmd.get_write_cmdmsg()[2]
        log.info("System disable global monitoring command: %s", str(disable_global_mon_cmd_msg))
        response = trx.send_recv_message(disable_global_mon_cmd_msg)
        decoded_response = decode_message(response)
        log.info("    response: 0x%04X: 0x%08X", decoded_response[0][0], decoded_response[0][1])
        
        while True:
            cmd.settings.device_cmd = 0 # device no-op
            cmd.settings.device_type = 1 # device monitoring
            cmd.settings.device_index = 16 # T sensor...
            device_no_op_cmd_msg = cmd.get_write_cmdmsg()[0]
            log.info("Device no-op command: %s", str(device_no_op_cmd_msg))
            response = trx.send_recv_message(device_no_op_cmd_msg)
            decoded_response = decode_message(response)
            log.info("    response: 0x%04X: 0x%08X", decoded_response[0][0], decoded_response[0][1])
        
            cmd.settings.device_cmd = 5 # device set and get
            log.debug("cmd map: %s", cmd.settings.generate_map())
            log.debug("       : %s", cmd.settings._mem_map)
            device_set_and_get_cmd_msg = cmd.get_write_cmdmsg()[0]
            log.info("Device get and set command: %s", str(device_set_and_get_cmd_msg))
            response = trx.send_recv_message(device_set_and_get_cmd_msg)
            decoded_response = decode_message(response)
            log.info("    response: 0x%04X: 0x%08X", decoded_response[0][0], decoded_response[0][1])
        
            read_echo_cmd_msg = cmd.get_read_cmdmsg()  # READ ECHO WORD
            log.info("READ ECHO WORD command: %s", str(read_echo_cmd_msg))
            response = trx.send_recv_message(read_echo_cmd_msg)
            decoded_response = decode_message(response)
            log.info("    response: 0x%04X: 0x%08X", decoded_response[0][0], decoded_response[0][1])
            time.sleep(0.5)
    
    
    
if __name__ == '__main__':
    main()
    