'''
Created on 8 May 2015

@author: Ulrik Pedersen
'''
from __future__ import unicode_literals, absolute_import
from future.utils import with_metaclass
import abc

from percival.detector.interface import IABCMeta

class IDeviceSettings(with_metaclass(abc.ABCMeta, IABCMeta)):
    '''
    classdocs
    '''
    __iproperties__ = ['num_words']
    __imethods__ = ['parse_map', 'generate_map']
    _iface_requirements = __imethods__ + __iproperties__
    
    @abc.abstractproperty
    def num_words(self):
        raise NotImplementedError
    
    @abc.abstractmethod
    def parse_map(self, words):
        raise NotImplementedError
    
    @abc.abstractmethod
    def generate_map(self):
        raise NotImplementedError

class HeaderInfo(object):
    """Represent the Header Info register bank"""
    num_words = 1
    
    def __init__(self):
        # Word 0
        self.eeprom_address = 0
        self.monitoring_channels_count = 0
        self.control_channels_count = 0
        
    def parse_map(self, words):
        raise NotImplementedError
        
    def generate_map(self):
        word0 = (self.eeprom_address << 16) | \
                (self.monitoring_channels_count << 8) | \
                (self.control_channels_count << 0)
        return [word0]

class ControlChannel(object):
    """Represent the map of Control Channels register bank"""
    num_words = 5
    
    def __init__(self):
        # Word 0
        self.board_type = 0
        self.component_family_id = 0
        self.device_i2c_bus_select = 0
        self.channel_device_id = 0
        self.channel_sub_address = 0
        self.device_address = 0
        
        # Word 1
        self.channel_range_max = 0
        self.channel_range_min = 0
        
        # Word 2
        self.channel_default_on = 0
        self.channel_default_off = 0
        
        # Word 3
        self.channel_monitoring = 0
        self.safety_exception_threshold = 0
        self.read_frequency = 0
    
        # Word 4
        self.power_status = False
        self.value = 0
        
class MonitoringChannel(object):
    """Represent the map of Monitoring Channel register bank"""
    num_words = 4
    
    def __init__(self):
        # Word 0
        self.board_type = 0
        self.component_family_id = 0
        self.device_i2c_bus_select = 0
        self.channel_device_id = 0
        self.channel_sub_address = 0
        self.device_address = 0

        # Word 1
        self.channel_ext_low_threshold = 0
        self.channel_ext_high_threshold = 0
        
        # Word 2
        self.channel_low_threshold = 0
        self.channel_high_threshold = 0
        
        # Word 3
        self.channel_monitoring = 0
        self.safety_exception_threshold = 0
        self.read_frequency = 0
        
IDeviceSettings.register(HeaderInfo)
IDeviceSettings.register(ControlChannel)
IDeviceSettings.register(MonitoringChannel)

