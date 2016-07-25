'''
Created on 20 May 2016

@author: Alan Greer
'''
from __future__ import print_function
from future.utils import raise_with_traceback

import os, time
import argparse
import zmq
import json

import logging
from percival.log import log

import os
import npyscreen
from percival.detector.ipc_reactor import IpcReactor
from percival.detector.ipc_channel import IpcChannel
from percival.detector.ipc_message import IpcMessage

board_ip_address = os.getenv("PERCIVAL_CARRIER_IP")


# This application class serves as a wrapper for the initialization of curses
# and also manages the actual forms of the application

class PercivalClientApp(npyscreen.NPSAppManaged):
    def __init__(self, ctrl_endpoint, status_endpoint):
        super(PercivalClientApp, self).__init__()
        self._ctrl_endpoint = ctrl_endpoint
        self._status_endpoint = status_endpoint
        self._poller = zmq.Poller()
        self._ctrl_channel = None
        self._status_channel = None
        self._current_value = None
        self._prev_value = None
        self._reply = None

    def onStart(self):
        self.keypress_timeout_default = 1
        self.registerForm("MAIN", IntroForm())
        self.registerForm("MAIN_MENU", MainMenu())

    def send_message(self, ipc_message):
        self._ctrl_channel.send(ipc_message.encode())
        pollevts = self._ctrl_channel.poll(1000)
        if pollevts == zmq.POLLIN:
            reply = IpcMessage(from_str=self._ctrl_channel.recv())
            if reply:
                self._reply = reply
                self._current_value = str(reply)

    def read_message(self, timeout):
        pollevts = self._ctrl_channel.poll(timeout)
        if pollevts == zmq.POLLIN:
            reply = IpcMessage(from_str=self._ctrl_channel.recv())
            return reply
        return None

    def read_status_message(self, timeout):
        pollevts = self._status_channel.poll(timeout)
        while pollevts == zmq.POLLIN:
            reply = IpcMessage(from_str=self._status_channel.recv())
            self._current_value = str(reply)
            pollevts = self._status_channel.poll(timeout)


# This form class defines the display that will be presented to the user.

class IntroForm(npyscreen.Form):
    def create(self):
        self.name = "Percival Carrier Board Client"
        self.add(npyscreen.TitleText, labelColor="LABELBOLD", name="Set the control and status endpoints of the application", value="", editable=False)
        self.ctrl = self.add(npyscreen.TitleText, name="Control Endpoint: ", value="")
        self.stat = self.add(npyscreen.TitleText, name="Status Endpoint: ", value="")

    def beforeEditing(self):
        self.ctrl.value = self.parentApp._ctrl_endpoint
        self.stat.value = self.parentApp._status_endpoint

    def afterEditing(self):
        self.parentApp._status_channel = IpcChannel(IpcChannel.CHANNEL_TYPE_SUB)
        self.parentApp._status_channel.connect(self.stat.value)
        self.parentApp._status_channel.subscribe("")
        self.parentApp._poller.register(self.parentApp._status_channel.socket, zmq.POLLIN)
        self.parentApp._ctrl_channel = IpcChannel(IpcChannel.CHANNEL_TYPE_PAIR)
        self.parentApp._ctrl_channel.connect(self.ctrl.value)
        self.parentApp.setNextForm("MAIN_MENU")


class MainMenu(npyscreen.FormBaseNew):
    def create(self):
        self.status_loop = False
        self.keypress_timeout = 1
        self.name = "Percival Carrier Board Client"
        self.t2 = self.add(npyscreen.BoxTitle, name="Main Menu:", relx=2, max_width=28)  # , max_height=20)
        self.t3 = self.add(npyscreen.BoxTitle, name="Response:", rely=2, relx=30)  # , max_width=45, max_height=20)

        self.t2.values = ["Read Board Parameters",
                          "Start Status Loop",
                          "Stop Status Loop",
                          "Monitor Device Setup",
                          "Send System Command",
                          "Exit"]
        self.t2.when_value_edited = self.button

    def button(self):
        selected = self.t2.entry_widget.value
        if selected == 0:
            msg = IpcMessage(IpcMessage.MSG_TYPE_CMD, IpcMessage.MSG_VAL_CMD_CONFIGURE)
            msg.set_param("list", "device")
            self.parentApp.send_message(msg)
            self.parentApp._boards = self.parentApp._reply.get_param("device")
        if selected == 1:
            msg = IpcMessage(IpcMessage.MSG_TYPE_CMD, IpcMessage.MSG_VAL_CMD_CONFIGURE)
            msg.set_param("status_loop", "run")
            self.parentApp.send_message(msg)
            self.status_loop = True
        if selected == 2:
            msg = IpcMessage(IpcMessage.MSG_TYPE_CMD, IpcMessage.MSG_VAL_CMD_CONFIGURE)
            msg.set_param("status_loop", "stop")
            self.parentApp.send_message(msg)
            self.status_loop = False
#            self.parentApp.setNextForm("SETUP_PROCESS")
#            self.editing = False
#            self.parentApp.switchFormNow()
#        if selected == 3:
#            self.parentApp.setNextForm("SETUP_FILE")
#            self.editing = False
#            self.parentApp.switchFormNow()
#        if selected == 4:
        if selected == 5:
            self.parentApp.setNextForm(None)
            self.parentApp.switchFormNow()

    def while_waiting(self):
        if self.status_loop == True:
            self.parentApp.read_status_message(0.05)
        if self.parentApp._current_value != self.parentApp._prev_value:
            self.t3.values = self.parentApp._current_value.split("\n")
            self.t3.display()
            self.parentApp._prev_value = self.parentApp._current_value
        self.t2.entry_widget.value = None
        self.t2.entry_widget._old_value = None
        self.t2.display()


def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--control", default="tcp://127.0.0.1:8888", help="Control endpoint")
    parser.add_argument("-s", "--status", default="tcp://127.0.0.1:8889", help="Status endpoint")
    args = parser.parse_args()
    return args


def main():
    args = options()
    log.info(args)

    app = PercivalClientApp(args.control, args.status)
    app.run()


if __name__ == '__main__':
    main()
