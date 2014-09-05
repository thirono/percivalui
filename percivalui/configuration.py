'''
Configuration of the Percival Detector system can be loaded from various files.

This module contain classes and functions to manage the loading of configurations.
'''
import logging
logger = logging.getLogger(__name__)

import os
from collections import OrderedDict
import ConfigParser

env_config_dir = "PERCIVAL_CONFIG_DIR"
'''
The environment variable PERCIVAL_CONFIG_DIR can optionally contain a path where
to look for configuration files at runtime. The current working directory and direct/full
paths will always override this directory, which will only be searched if the file
cannot be found
'''

def find_file(filename, env=None):
    '''Search for a file and return the full path if it can be found.
    
    Raises IOError if a file of the given name cannot be found.
    
    :param filename: The filename to search for. Can be relative or full path.
    :param env: The name of an environment variable which can contain a list of
                colon-separated directories. These directories (if any) will be
                searched for the :param:`filename` if it cannot be found.
    :returns: An absolute path to the file of the same name.
    '''
    
    # Check if the filename exist as a relative or absolute path
    if os.path.isfile(filename):
        return os.path.abspath(filename)
    
    # Check  if the file exist in one of the search paths, indicated by
    # the user in an environemnt variable
    for path in os.getenv(env_config_dir, "").split(":"):
        fn = os.path.abspath( os.path.join([path, filename]) )
        if os.path.isfile(fn):
            return fn
    
    # All other searches failed. We cant find this file. Raise exception.
    raise IOError

class PeripheryBoardConfiguration:
    '''Load and maintain the Periphery Board configuration data'''
    
    def __init__(self, config_file = None):
        '''Constructor. Optionally load the configuration file data
        
        :param config_file: The name of the configuration file to load. Full or
                            relative paths is supported. If the file cannot be
                            found, the directories listed in environment variable 
                            :obj:`env_config_dir` are searched for the file. 
        '''
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self.cfg_filename = None
        
        # The data sections from the ini files are ordered in categories:
        self.board_header = dict()
        self.entry_count = dict()
        self.components = list()
        self.devices = list()
        self.control_channels = list()
        self.monitoring_channels = list()
        
        
    def load_ini(self, config_file):
        self.cfg_filename = find_file( config_file )
        
        self.conf = ConfigParser.SafeConfigParser(dict_type=OrderedDict)
        if self.cfg_filename:
            self.conf.read( self.cfg_filename )

        self.board_header = 