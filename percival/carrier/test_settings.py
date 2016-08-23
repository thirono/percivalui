'''
Created on 13 June 2016

@author: gnx91527
'''
from __future__ import unicode_literals, absolute_import

import unittest, sys, logging
from mock import MagicMock
from builtins import bytes

class TestSettings(unittest.TestCase):

    def setUp(self):
        # Perform any setup here
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(logging.DEBUG)

    def TestControlChannel(self):
        # Stub
        self.log.debug("Test Stub")
