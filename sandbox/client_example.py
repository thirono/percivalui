"""
Percival client example application with ncurses text-gui interface

"""
from __future__ import print_function

import os
import traceback
import argparse
import zmq
import npyscreen

from percival.log import get_exclusive_file_logger
from percival.detector.ipc_channel import IpcChannel
from percival.detector.ipc_message import IpcMessage
from percival.carrier import const

board_ip_address = os.getenv("PERCIVAL_CARRIER_IP")


# This application class serves as a wrapper for the initialization of curses
# and also manages the actual forms of the application

class PercivalClientApp(npyscreen.NPSAppManaged):
    def __init__(self, ctrl_endpoint, status_endpoint):
        super(PercivalClientApp, self).__init__()
        self.ctrl_endpoint = ctrl_endpoint
        self.status_endpoint = status_endpoint
        self.poller = zmq.Poller()
        self.ctrl_channel = None
        self.status_channel = None
        self.current_value = None
        self.prev_value = None
        self.reply = None

    def onStart(self):
        self.keypress_timeout_default = 1
        self.registerForm("MAIN", IntroForm())
        self.registerForm("MAIN_MENU", MainMenu())
        self.registerForm("SYS_CMD", SendSystemCommand())

    def send_message(self, ipc_message):
        log.debug("sending message: %s", ipc_message)
        self.ctrl_channel.send(ipc_message.encode())
        pollevts = self.ctrl_channel.poll(1000)
        log.debug("poll event: %s", pollevts)
        if pollevts == zmq.POLLIN:
            reply = IpcMessage(from_str=self.ctrl_channel.recv())
            log.debug("Message reply: %s", reply)
            if reply:
                self.reply = reply
                self.current_value = str(reply)
        elif pollevts == 0:
            log.error("poll timeout without reply")
            self.current_value = "ERROR: poll timeout without reply"

    def read_message(self, timeout):
        pollevts = self.ctrl_channel.poll(timeout)
        if pollevts == zmq.POLLIN:
            reply = IpcMessage(from_str=self.ctrl_channel.recv())
            return reply
        return None

    def read_status_message(self, timeout):
        pollevts = self.status_channel.poll(timeout)
        while pollevts == zmq.POLLIN:
            reply = IpcMessage(from_str=self.status_channel.recv())
            self.current_value = str(reply)
            pollevts = self.status_channel.poll(timeout)


# This form class defines the display that will be presented to the user.
class IntroForm(npyscreen.Form):
    def create(self):
        self.name = "Percival Carrier Board Client"
        self.add(npyscreen.TitleText, labelColor="LABELBOLD", name="Set the control and status endpoints of the application", value="", editable=False)
        self.ctrl = self.add(npyscreen.TitleText, name="Control Endpoint: ", value="")
        self.stat = self.add(npyscreen.TitleText, name="Status Endpoint: ", value="")

    def beforeEditing(self):
        self.ctrl.value = self.parentApp.ctrl_endpoint
        self.stat.value = self.parentApp.status_endpoint

    def afterEditing(self):
        log.debug("Connecting to IPC channel (status): %s", self.stat.value)
        self.parentApp.status_channel = IpcChannel(IpcChannel.CHANNEL_TYPE_SUB)
        self.parentApp.status_channel.connect(self.stat.value)
        self.parentApp.status_channel.subscribe("")
        log.debug("Connected (status): %s", self.parentApp.status_channel)
        self.parentApp.poller.register(self.parentApp.status_channel.socket, zmq.POLLIN)

        log.debug("Connecting to IPC channel (control): %s", self.ctrl.value)
        self.parentApp.ctrl_channel = IpcChannel(IpcChannel.CHANNEL_TYPE_PAIR)
        self.parentApp.ctrl_channel.connect(self.ctrl.value)
        log.debug("Connected (control): %s", self.parentApp.ctrl_channel)
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
                          "List Control Devices",
                          "List Monitor Devices",
                          "Send System Command",
                          "Exit"]
        self.t2.when_value_edited = self.button

    def button(self):
        selected = self.t2.entry_widget.value
        try:
            if selected == 0:
                msg = IpcMessage(IpcMessage.MSG_TYPE_CMD, IpcMessage.MSG_VAL_CMD_CONFIGURE)
                msg.set_param("list", "device")
                self.parentApp.send_message(msg)
                self.parentApp.boards = self.parentApp.reply.get_param("device")
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
            if selected == 3:
                msg = IpcMessage(IpcMessage.MSG_TYPE_CMD, IpcMessage.MSG_VAL_CMD_CONFIGURE)
                msg.set_param("list", "controls")
                self.parentApp.send_message(msg)
            if selected == 4:
                msg = IpcMessage(IpcMessage.MSG_TYPE_CMD, IpcMessage.MSG_VAL_CMD_CONFIGURE)
                msg.set_param("list", "monitors")
                self.parentApp.send_message(msg)
            if selected == 5:
                self.parentApp.setNextForm("SYS_CMD")
                self.editing = False
                self.parentApp.switchFormNow()
            if selected == 6:
                self.parentApp.setNextForm(None)
                self.parentApp.switchFormNow()
        except Exception as e:
            log.exception(e)
            tb = traceback.format_exc()
            self.parentApp.current_value = "ERROR:\n------------------------\n" + tb

    def while_waiting(self):
        if self.status_loop == True:
            self.parentApp.read_status_message(0.05)
        if self.parentApp.current_value != self.parentApp.prev_value:
            self.t3.values = self.parentApp.current_value.split("\n")
            self.t3.display()
            self.parentApp.prev_value = self.parentApp.current_value
        self.t2.entry_widget.value = None
        self.t2.entry_widget._old_value = None
        self.t2.display()


class SendSystemCommand(npyscreen.FormBaseNew):
    def create(self):
        self.keypress_timeout = 1
        self.name = "Percival Carrier Board Client"
        self.t2 = self.add(npyscreen.BoxTitle, name="Select system command to send:")

        # Add all available system commands to the select list - and an exit (no-op) option at the end
        self.t2.values = [cmd.name for cmd in const.SystemCmd] + ["Exit"]
        self.t2.when_value_edited = self.button

    def button(self):
        selected = self.t2.entry_widget.value
        if selected is not None:
            self.t2.entry_widget.value = None
            self.t2.entry_widget._old_value = None
            if self.t2.values[selected] == "Exit":
                self.parentApp.setNextForm("MAIN_MENU")
                self.editing = False
                self.parentApp.switchFormNow()
            else:
                msg = IpcMessage(IpcMessage.MSG_TYPE_CMD, IpcMessage.MSG_VAL_CMD_CONFIGURE)
                msg.set_param("system_command", self.t2.values[selected])
                self.parentApp.send_message(msg)
                self.parentApp.setNextForm("MAIN_MENU")
                self.editing = False
                self.parentApp.switchFormNow()


def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--control", default="tcp://127.0.0.1:8888", help="Control endpoint")
    parser.add_argument("-s", "--status", default="tcp://127.0.0.1:8889", help="Status endpoint")
    args = parser.parse_args()
    return args


def main():
    global log
    log = get_exclusive_file_logger("client_example.log")

    args = options()
    log.info(args)

    app = PercivalClientApp(args.control, args.status)
    app.run()


if __name__ == '__main__':
    main()
