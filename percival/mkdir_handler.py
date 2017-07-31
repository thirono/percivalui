import os
from logging.handlers import RotatingFileHandler


class MkDirRotatingFileHandler(RotatingFileHandler):
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=0):
        dir = os.path.dirname(filename)
        if not os.path.exists(dir):
            os.makedirs(dir)
        RotatingFileHandler.__init__(self, filename, mode, maxBytes, backupCount, encoding, delay)

