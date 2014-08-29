'''
The detector interface module contains a number of abstract interface definitions
which are to be implemented by classes that support control and communication
with detectors.

The interface classes do not implement any real functionality, but are used to define
the methods (and their args) and properties, required to support a certain
interface.

The interface classes rely on the python :mod:`abc` module to support Abstract Base
Classes
'''

import abc
from inspect import ismethod, getargspec

class IABCMeta(object):
    '''
    Abstract Base Meta Class which implements checking for required methods and
    properties, even when the class is not directly subclassed.
    The Interface class which uses this metaclass will need to define a property
    called :py:attr:`_iface_requirements` which is a list of properties that must be implemented.
    
    This class is intended to work together with the :py:class:`abc.ABCMeta` class:
    Subclass :class:`IABCMeta` into your own class and set the :py:const:`__metaclass__` = :py:class:`abc.ABCMeta`
    The :py:meth:`__subclasshook__` will automatically be called when a class
    interface need to be verified.
    '''
    
    _iface_requirements = []
    '''Interface requirements list. The memebers listed here must be implemented 
       by subclasses'''
    
    @classmethod
    def __subclasshook__(cls, C):
        '''Iterate through the :py:attr:`_iface_requirements` list of members and check
        whether they are implemented by the current class or parent.
        
        For requirement functions:
        Check if the functions arguments match the required arguments
        of the interface function.
        
        Rules for implementation of interface functions:
            1) Must have at least the main (non-defaulted) named args
            2) Can extend the list of arguments
            
        Default value arguments are discouraged in interfaces as the
        interface does not implement any functionality. Implementations
        can assign default values to the arguments if desired.
        '''
        if not cls._iface_requirements:
            return NotImplemented
        
        checks = []
        for req in cls._iface_requirements:
            has_req = any(req in B.__dict__ for B in C.__mro__)
            result = has_req
            if has_req:
                if ismethod(getattr(cls, req)):
                    # Check if the functions arguments match the required arguments
                    interface_func_args = getargspec( getattr(cls, req) ).args
                    impl_func_args = getargspec(getattr(C,req)).args
                    try:
                        result = interface_func_args == impl_func_args[:len(interface_func_args)]
                    except:
                        result = False
            checks.append(result)
        return not False in checks

class IDetector(IABCMeta):
    '''
    Abstract Interface to a detector class
    '''
    __metaclass__ = abc.ABCMeta
    __iproperties__ = ['exposure']
    __imethods__ = ['acquire']
    _iface_requirements = __imethods__ + __iproperties__
    
    @property
    def exposure(self):
        raise NotImplementedError
    
    @abc.abstractmethod
    def acquire(self, exposure, nframes):
        '''
        Start the detector acquiring data
        '''
        raise NotImplementedError
    
class IParameter(object):
    '''Pure abstract interface to describe a detector parameter'''
    __metaclass__ = abc.ABCMeta
    
    @property
    def value(self):
        return self._value
    @value.setter
    def value(self, value):
        self._value = value
    

class IControl(object):
    __metaclass__ = abc.ABCMeta
    

class IData(object):
    __metaclass__ = abc.ABCMeta
    
    def get_filename(self):
        return self.filename
    def set_filename(self, fname):
        self.filename = fname
    filename = abc.abstractproperty(get_filename, set_filename)
    
    