"""
Created on 22nd July 2016

:author: Alan Greer
"""
import logging
import time
import traceback
from odin.adapters.adapter import ApiAdapter, ApiAdapterResponse, request_types, response_types
from percival.detector.detector import PercivalDetector
from percival.detector.command import Command
from concurrent import futures
from tornado.ioloop import IOLoop
from tornado.concurrent import run_on_executor


class PercivalAdapter(ApiAdapter):
    """
    PercivalAdapter class

    This class provides the adapter interface between the ODIN server and the PERCIVAL detector system,
    transforming the REST-like API HTTP verbs into the appropriate EXCALIBUR detector control actions
    """

    # Thread executor used for background tasks
    executor = futures.ThreadPoolExecutor(max_workers=1)

    def __init__(self, **kwargs):
        """
        Initialise the PercivalAdapter object

        :param kwargs:
        """
        self._log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        super(PercivalAdapter, self).__init__(**kwargs)

        self._log.debug("init kwargs: %s", kwargs)
        ini_file = None
        if 'config_file' in kwargs:
            ini_file = kwargs['config_file']

        self._detector = PercivalDetector(ini_file, False, False)
        self._detector.set_global_monitoring(True)
        self._auto_read = False
        self.status_update(0.1)

    @run_on_executor
    def status_update(self, task_interval):
        if self._detector:
            if self._auto_read:
                self._detector.update_status()
        time.sleep(task_interval)
        IOLoop.instance().add_callback(self.status_update, task_interval)

    @request_types('application/json')
    @response_types('application/json', default='application/json')
    def get(self, path, request):

        """
        Implementation of the HTTP GET verb for ExcaliburAdapter

        :param path: URI path of the GET request
        :param request: Tornado HTTP request object
        :return: ApiAdapterResponse object to be returned to the client
        """

        self._log.debug("GET %s", request)

        # Create a new Percival Command object
        cmd = Command(request)
        response = self._detector.execute_command(cmd)

        # If the driver status has been requested append the auto_read status
        if "driver" in cmd.command_name:
            response["auto_read"] = self._auto_read

        status_code = 200

        return ApiAdapterResponse(response, status_code=status_code)

    @request_types('application/json')
    @response_types('application/json', default='application/json')
    def put(self, path, request):  # pylint: disable=W0613

        """
        Implementation of the HTTP PUT verb for ExcaliburAdapter

        :param path: URI path of the PUT request
        :param request: Tornado HTTP request object
        :return: ApiAdapterResponse object to be returned to the client
        """

        self._log.debug("PUT %s", request)
        self._log.debug("PUT %s", request.body)

        status_code = 200
        response = {'response': 'Submitted',
                    'error': '',
                    'command': 'Unknown',
                    'param_names': 'Unknown',
                    'parameters': 'Unknown',
                    'time': 'Unknown'}

        # Create a new Percival Command object
        try:
            cmd = Command(request)
            response['command'] = cmd.command_name
            response['param_names'] = cmd.param_names
            response['parameters'] = cmd.parameters
            response['time'] = cmd.command_time
            if 'start' in cmd.command_name:
                self._auto_read = True
            elif 'stop' in cmd.command_name:
                self._auto_read = False
            else:
                #cmd_response = self._detector.execute_command(cmd)
                self._detector.queue_command(cmd)
                # Merge the response from the command execution
                #for key in cmd_response:
                #    response[key] = cmd_response[key]
        except Exception as ex:
            # Return an error condition with the exception message
            # status_code = 500
            response['response'] = 'Failed'
            response['error'] = "{} => {}".format(ex.args, traceback.format_exc())

        self._log.debug(response)

        return ApiAdapterResponse(response, status_code=status_code)

    @request_types('application/json')
    @response_types('application/json', default='application/json')
    def delete(self, path, request):  # pylint: disable=W0613
        """
        Implementation of the HTTP DELETE verb for ExcaliburAdapter

        :param path: URI path of the DELETE request
        :param request: Tornado HTTP request object
        :return: ApiAdapterResponse object to be returned to the client
        """
        response = {'response': '{}: DELETE on path {}'.format(self.name, path)}
        status_code = 200

        self._log.debug(response)

        return ApiAdapterResponse(response, status_code=status_code)

    def cleanup(self):
        if self._detector:
            self._detector.cleanup()
