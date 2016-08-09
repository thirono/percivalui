from __future__ import print_function

import argparse
import json
import npyscreen
import requests

from percival.log import get_exclusive_file_logger


class OdinClientApp(npyscreen.NPSAppManaged):
    def __init__(self, url, api):
        super(OdinClientApp, self).__init__()
        self._url = url
        self._api = api

    def onStart(self):
        self.keypress_timeout_default = 1
        self.registerForm("MAIN", IntroForm())
        self.registerForm("MAIN_MENU", MainMenu())

    def build_url(self):
        return self._url + "/api/" + self._api + "/"

    def send_message(self, msg):
        full_msg = self.build_url() + msg
        log.debug("Sending msg: %s", full_msg)
        try:
            result = requests.get(full_msg,
                                  headers={
                                      'Content-Type': 'application/json',
                                      'Accept': 'application/json'
                                  }).json()
        except requests.exceptions.RequestException:
            result = {
                "error": "Exception during HTTP request, check address and Odin server instance"
            }
            log.exception(result['error'])
        return result


class IntroForm(npyscreen.Form):
    def create(self):
        self.name = "Odin Client"
        self.add(npyscreen.TitleText, labelColor="LABELBOLD", name="Set the URL and API version for the Odin server", value="", editable=False)
        self.url = self.add(npyscreen.TitleText, name="URL: ", value="")
        self.api = self.add(npyscreen.TitleText, name="API: ", value="")

    def beforeEditing(self):
        self.url.value = self.parentApp._url
        self.api.value = self.parentApp._api

    def afterEditing(self):
        self.parentApp._url = self.url.value
        self.parentApp._api = self.api.value
        self.parentApp.setNextForm("MAIN_MENU")


class MainMenu(npyscreen.FormBaseNew):
    def create(self):
        self.keypress_timeout = 1
        self.name = "Odin Client"
        self.t2 = self.add(npyscreen.BoxTitle, name="Main Menu:", relx=2, max_width=28)
        self.t3 = self.add(npyscreen.BoxTitle, name="Response:", rely=2, relx=30)

        self.t2.values = ["Read Board Parameters",
                          "Read Board Status",
                          "Read Monitor List",
                          "Read Control List",
                          "Read VCH0",
                          "Read Temperature1",
                          "Exit"]
        self.t2.when_value_edited = self.button

    def button(self):
        selected = self.t2.entry_widget.value
        if selected == 0:
            reply = self.parentApp.send_message("percival/device")
            self.t3.values = json.dumps(reply, sort_keys=True, indent=4, separators=(',', ': ')).split("\n")
            self.t3.display()
        if selected == 1:
            reply = self.parentApp.send_message("percival/status")
            self.t3.values = json.dumps(reply, sort_keys=True, indent=4, separators=(',', ': ')).split("\n")
            self.t3.display()
        if selected == 2:
            reply = self.parentApp.send_message("percival/monitors")
            self.t3.values = json.dumps(reply, sort_keys=True, indent=4, separators=(',', ': ')).split("\n")
            self.t3.display()
        if selected == 3:
            reply = self.parentApp.send_message("percival/controls")
            self.t3.values = json.dumps(reply, sort_keys=True, indent=4, separators=(',', ': ')).split("\n")
            self.t3.display()
        if selected == 4:
            reply = self.parentApp.send_message("percival/VCH0")
            self.t3.values = json.dumps(reply, sort_keys=True, indent=4, separators=(',', ': ')).split("\n")
            self.t3.display()
        if selected == 5:
            reply = self.parentApp.send_message("percival/Temperature1")
            self.t3.values = json.dumps(reply, sort_keys=True, indent=4, separators=(',', ': ')).split("\n")
            self.t3.display()
        if selected == 6:
            self.parentApp.setNextForm(None)
            self.parentApp.switchFormNow()

    def while_waiting(self):
        self.t2.entry_widget.value = None
        self.t2.entry_widget._old_value = None
        self.t2.display()


def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", default="http://127.0.0.1:8888", help="Address of Odin server")
    parser.add_argument("-a", "--api", default="0.1", help="API version")
    args = parser.parse_args()
    return args


def main():
    global log
    log = get_exclusive_file_logger("odin_client.log")
    args = options()
    log.info(args)

    app = OdinClientApp(args.url, args.api)
    app.run()


if __name__ == '__main__':
    main()
