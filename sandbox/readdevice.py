'''
Created on 19 May 2015

@author: up45
'''
from __future__ import print_function

from percival.log import log

from percival.carrier.registers import UARTRegister
from percival.carrier.txrx import TxRx, TxRxContext, TxMessage
from percival.carrier.encoding import (encode_message, encode_multi_message, decode_message)

board_ip_address = "percival2.diamond.ac.uk"

def main():
    log.debug("read device...")
    
    #with TxRxContext(board_ip_address) as trx:
    
    cmd = UARTRegister(0x00EC)  # Command register
    cmd.settings.parse_map([0,0,0]) # initialise all registers to 0
    
    # First generate and send a no-op system command
    cmd.settings._mem_map["system_cmd"].value = 0 # no-op system command
    cmd.settings._mem_map["system_cmd_data"].value = 0  # not used
    no_op_cmd_msg = cmd.get_write_cmdmsg()[2]
    log.info("System no-op command: %s", str(no_op_cmd_msg))
    
   
    cmd.settings._mem_map["system_cmd"].value = 2 # disable global monitoring
    disable_global_mon_cmd_msg = cmd.get_write_cmdmsg()[2]
    log.info("System disable global monitoring command: %s", str(disable_global_mon_cmd_msg))
    
    cmd.settings._mem_map["device_cmd"].value = 0 # device no-op
    cmd.settings._mem_map["device_type"].value = 1 # device monitoring
    cmd.settings._mem_map["device_index"].value = 2 # T sensor...
    device_no_op_cmd_msg = cmd.get_write_cmdmsg()[0]
    log.info("Device no-op command: %s", str(device_no_op_cmd_msg))

    cmd.settings._mem_map["device_cmd"].value = 5 # device set and get
    log.debug("cmd map: %s", cmd.settings.generate_map())
    log.debug("       : %s", cmd.settings._mem_map)
    device_set_and_get_cmd_msg = cmd.get_write_cmdmsg()[0]
    log.info("Device get and set command: %s", str(device_set_and_get_cmd_msg))
    
    read_echo_cmd_msg = cmd.get_read_cmdmsg()  # READ ECHO WORD
    log.info("READ ECHO WORD command: %s", str(read_echo_cmd_msg))
    
    
    
    
if __name__ == '__main__':
    main()
    