from __future__ import print_function

import requests
import time
import getpass
from datetime import datetime

from percival.log import log


class PercivalClient(object):
    def __init__(self, address="127.0.0.1:8888", api=0.1):
        self._address = address
        self._api = api
        self._url = "http://" + str(self._address) + "/api/" + str(self._api) + "/percival/"
        self._user = getpass.getuser()

    def send_command(self, command, command_id="python_script", arguments=None):
        try:
            url = self._url + command
            log.debug("Sending msg to: %s", url)
            result = requests.put(url,
                                  data=arguments,
                                  headers={
                                      'Content-Type': 'application/json',
                                      'Accept': 'application/json',
                                      'User': self._user,
                                      'Creation-Time': str(datetime.now()),
                                      'User-Agent': command_id
                                  }).json()
        except requests.exceptions.RequestException:
            result = {
                "error": "Exception during HTTP request, check address and Odin server instance"
            }
            log.exception(result['error'])

        return result

    def get_status(self, status_item, arguments=None):
        try:
            url = self._url + status_item
            log.debug("Sending msg to: %s", url)
            result = requests.get(url,
                                  data=arguments,
                                  headers={
                                      'Content-Type': 'application/json',
                                      'Accept': 'application/json',
                                      'User': self._user,
                                      'Creation-Time': str(datetime.now())
                                  }).json()
        except requests.exceptions.RequestException:
            result = {
                "error": "Exception during HTTP request, check address and Odin server instance"
            }
            log.exception(result['error'])

        return result

    def wait_for_command_completion(self, wait_time=1.0):
        response = None
        command_active = True
        while command_active:
            response = self.get_status('action')
            log.debug(response)
            if response['response'] == 'Active':
                time.sleep(wait_time)
            else:
                command_active = False
        return response

    def send_configuration(self, config_type, config_contents, command_id="python_script"):
        arguments = {
            'config_type': config_type,
            'config': config_contents.replace('=', '::')
        }
        return self.send_command('cmd_load_config', command_id, arguments)

    def send_system_command(self, system_command, command_id="python_script"):
        arguments = {
            'name': system_command.name
        }
        return self.send_command('cmd_system_command', command_id, arguments)

    def apply_setpoint(self, set_point, command_id="python_script"):
        arguments = {
            'setpoint': set_point
        }
        return self.send_command('cmd_apply_setpoint', command_id, arguments)
