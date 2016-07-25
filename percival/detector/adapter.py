"""
Created on 22nd July 2016

:author: Alan Greer
"""
import logging
from odin.adapters.adapter import ApiAdapter, ApiAdapterResponse, request_types, response_types
from percival.detector.detector import PercivalDetector


class PercivalAdapter(ApiAdapter):
    """
    PercivalAdapter class

    This class provides the adapter interface between the ODIN server and the PERCIVAL detector system,
    transforming the REST-like API HTTP verbs into the appropriate EXCALIBUR detector control actions
    """

    def __init__(self, **kwargs):
        """
        Initialise the PercivalAdapter object

        :param kwargs:
        """
        super(PercivalAdapter, self).__init__(**kwargs)

        self.detector = PercivalDetector()
        self.detector.initialise_board()
        self.detector.load_channels()
        self.detector.set_global_monitoring(True)

    @request_types('application/json')
    @response_types('application/json', default='application/json')
    def get(self, path, request):

        """
        Implementation of the HTTP GET verb for ExcaliburAdapter

        :param path: URI path of the GET request
        :param request: Tornado HTTP request object
        :return: ApiAdapterResponse object to be returned to the client
        """

        logging.debug("%s", request)

        # Split the path by /
        options = path.split("/")
        # Check the options for the list keyword
        if options[0] == "list":
            response = self.detector.list(options[1])
            status_code = 200
        elif options[0] == "status":
            response = self.detector.update_status()
            status_code = 200
        else:
            response = {'response' : '{}: GET on path {}'.format(self.name, path)}
            status_code = 200

        logging.debug(response)

        return ApiAdapterResponse(response, status_code=status_code)

    @request_types('application/json')
    @response_types('application/json', default='application/json')
    def put(self, path, request):

        """
        Implementation of the HTTP PUT verb for ExcaliburAdapter

        :param path: URI path of the PUT request
        :param request: Tornado HTTP request object
        :return: ApiAdapterResponse object to be returned to the client
        """

        response = {'response': '{}: PUT on path {}'.format(self.name, path)}
        status_code = 200

        logging.debug(response)

        return ApiAdapterResponse(response, status_code=status_code)


    @request_types('application/json')
    @response_types('application/json', default='application/json')
    def delete(self, path, request):
        """
        Implementation of the HTTP DELETE verb for ExcaliburAdapter

        :param path: URI path of the DELETE request
        :param request: Tornado HTTP request object
        :return: ApiAdapterResponse object to be returned to the client
        """

        response = {'response': '{}: DELETE on path {}'.format(self.name, path)}
        status_code = 200

        logging.debug(response)

        return ApiAdapterResponse(response, status_code=status_code)
