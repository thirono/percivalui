'''
Created on 19 May 2015

@author: Ulrik Pedersen
'''
from __future__ import print_function

import os, time, binascii, signal
import numpy, h5py

from percival.log import log

from percival.carrier.registers import UARTRegister, BoardRegisters, BoardTypes
from percival.carrier.devices import ReadValue, DeviceFamily, DeviceFunction, DeviceCmd
from percival.carrier.txrx import TxRx, TxRxContext, TxMessage
from percival.carrier.encoding import (encode_message, encode_multi_message, decode_message)

board_ip_address = os.getenv("PERCIVAL_CARRIER_IP")

class CarrierBoard:
    pass

class ControlChannel:
    def __init__(self, txrx, device_family, device_index, settings, board):
        '''Constructor

            :param txrx: Percival communication context
            :type  txrx: TxRx
            :param device_family: The type of device
            :type  device_family: DeviceFamily
            :param device_index: Control device channel index
            :type  device_index: int

        '''
        self._txrx = txrx
        self.device_family = device_family
        print(self.device_family)
        if self.device_family.value.function != DeviceFunction.control:
            raise TypeError("Not a control device")
        self.device_index = device_index

        self._reg_command = UARTRegister(0x00F8)
        self._reg_command.initialize_map([0,0,0])
        self._reg_command.fields.device_type = self.device_family.value.function.value
        self._reg_command.fields.device_index = self.device_index

        self._reg_echo = UARTRegister(0x0139)

        addr_header, addr_control, addr_monitoring = BoardRegisters[board]
        self._reg_control_settings = UARTRegister(addr_control)
        self._reg_control_settings.initialize_map(settings)
        log.debug(self._reg_control_settings.get_write_cmdmsg(device_index=device_index))

    def read_echo_word(self):
        echo_cmd_msg = self._reg_echo.get_read_cmdmsg()
        response = self._txrx.send_recv_message(echo_cmd_msg)
        return response

    def get_command_msg(self, cmd):
        if not self.device_family.value.supports_cmd(cmd):
            raise TypeError("Device family does not support command %s"%cmd)
        self._reg_command.fields.device_cmd = cmd.value
        cmd_msg = self._reg_command.get_write_cmdmsg(eom=True)[0]
        return cmd_msg

    def command(self, cmd):
        cmd_msg = self.get_command_msg(cmd)
        response = self._txrx.send_recv_message(cmd_msg)
        return response

    def cmd_no_operation(self):
        result = self.command(DeviceCmd.no_operation)
        return result

    def cmd_set_and_get_value(self):
        result = self.command(DeviceCmd.set_and_get_value)
        return result

    def cmd_control_set_value(self, value):
        self._reg_control_settings.fields.value = value
        cmd_msg = self._reg_control_settings.get_write_cmdmsg(eom=True, device_index=self.device_index)
        return cmd_msg

    def set_value(self, value):
        self.cmd_no_operation()
        self.cmd_control_set_value(value)
        self.cmd_no_operation()
        self.cmd_set_and_get_value()
        result = self.read_echo_word()
        return result


class BoardSettings:
    def __init__(self, txrx, board):
        self.txrx = txrx
        addr_header, addr_control, addr_monitoring = BoardRegisters[board]

        self._reg_control_settings = UARTRegister(addr_control)

    def get_control_settings(self):
        cmd_msg = self._reg_control_settings.get_read_cmdmsg()
        response = self.txrx.send_recv_message(cmd_msg)
        result = decode_message(response)
        return result


if __name__ == '__main__':
    with TxRxContext(board_ip_address) as trx:
        bs = BoardSettings(trx, BoardTypes.carrier)
        carrier_ctrl_settings = bs.get_control_settings()
        log.info(carrier_ctrl_settings)

        cc_settings = [val for addr, val in carrier_ctrl_settings][1:1+4]
        log.info(cc_settings)
        cc = ControlChannel(trx, DeviceFamily.AD5669, 1, cc_settings, BoardTypes.carrier)
        log.info(cc.cmd_no_operation())
        log.info(cc.cmd_set_and_get_value())
        log.info(cc.cmd_control_set_value(7))

        log.info(cc.set_value(9))

        log.info(bs.get_control_settings())

