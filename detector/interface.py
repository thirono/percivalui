'''
Created on 25 Jul 2014

@author: up45
'''
import abc
from types import UnboundMethodType 
from inspect import ismethod, getargspec

class IABCMeta(object):
    '''
    Abstract Base Meta Class which implements checking for required methods and
    properties, even when the class is not directly subclassed.
    The Interface class which uses this metaclass will need to define a property
    called __iface_requirements__ which is a list of properties that must be implemented.
    '''
    @classmethod
    def __subclasshook__(cls, C):
        print "__subclasshook__ called: %s, %s"%(cls,C)
        if hasattr(cls, '__iface_requirements__'):
            checks = []
            for req in cls.__iface_requirements__:
                has_req = any(req in B.__dict__ for B in C.__mro__)
                result = has_req
                if has_req:
                    if ismethod(getattr(cls, req)):
                        # Check if the functions arguments match the required arguments
                        # of the interface function
                        # Rules for implementation of interface functions:
                        # 1) Must have at least the main (non-defaulted) named args
                        # 2) Can extend the list of arguments
                        # Default value arguments are discouraged in interfaces as the
                        # interface does not implement any functionality. Implementations
                        # can assign default values to the arguments if desired.
                        interface_func_args = getargspec( getattr(cls, req) ).args
                        impl_func_args = getargspec(getattr(C,req)).args
                        print req, getargspec( getattr(cls, req) ),  getargspec(getattr(C,req))
                        try:
                            result = interface_func_args == impl_func_args[:len(interface_func_args)]
                        except:
                            result = False
                checks.append(result)
            print checks
            return not False in checks
        return NotImplemented

class IDetector(IABCMeta):
    '''
    Abstract Interface to a detector class
    '''
    __metaclass__ = abc.ABCMeta
    __iproperties__ = ['exposure']
    __imethods__ = ['acquire']
    __iface_requirements__ = __imethods__ + __iproperties__
    
    @property
    def exposure(self):
        raise NotImplementedError
    
    @abc.abstractmethod
    def acquire(self, exposure, nframes):
        '''
        Start the detector acquiring data
        '''
        raise NotImplementedError
    


class IControl(object):
    __metaclass__ = abc.ABCMeta
    

class IData(object):
    __metaclass__ = abc.ABCMeta
    
    def get_filename(self):
        return self.filename
    def set_filename(self, fname):
        self.filename = fname
    filename = abc.abstractproperty(get_filename, set_filename)
    
    