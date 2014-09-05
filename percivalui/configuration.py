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
    full_name = None
    if os.path.isfile(filename):
        return os.path.abspath(filename)
    ###### TODO: This function is not yet complete, but I have to go home and have a nice weekend!

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
        
    def load_ini(self, config_file):
        if os.path.isfile(config_file):
            self.config_filename = os.path.abspath(config_file)
        else:
            search_dir = os.getenv(env_config_dir, "")
            
        
        self.conf = ConfigParser.SafeConfigParser(dict_type=OrderedDict)
        if self.config_filename:
            self.conf.read( self.config_filename )
        ###### TODO: This function is not yet complete, but I have to go home and have a nice weekend!
