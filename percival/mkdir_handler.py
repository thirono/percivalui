"""
Created on 1 August 2017

@author: Alan Greer
"""
import os
from logging.handlers import RotatingFileHandler


class MkDirRotatingFileHandler(RotatingFileHandler):
    """
    Subclass of RotatingFileHandler that attempts to create any directories required by the log file.
    """
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=0):
        dir = os.path.dirname(filename)
        if not os.path.exists(dir):
            os.makedirs(dir)
        RotatingFileHandler.__init__(self, filename, mode, maxBytes, backupCount, encoding, delay)

