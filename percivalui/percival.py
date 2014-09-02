'''
The main PercivalUI module

'''

import logging
logger = logging.getLogger(__name__)

import detector.parameter
from detector.interface import IDetector, IControl, IData

 
class DACs:
    some_gain = detector.parameter.Observable('some_gain')

class CarrierBoard(object):
    def __init__(self):
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self.dacs = DACs

class MezzanineBoard(IData):
    def __init__(self):
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        
    ### Implemetation of the IData interface ###
    _filename = ""
    def get_filename(self):
        return self._filename
    def set_filename(self, fname):
        self._filename = fname
    filename = property(get_filename, set_filename)
    
    _datasetname = ""
    def get_datasetname(self):
        return self._datasetname
    def set_datasetname(self):
        return self._datasetname
    datasetname = property(get_datasetname, set_datasetname)

    def start_capture(self, filename, nframes):
        '''
        Implements interface: :func:`detector.interface.IData.start_capture()`
        '''
        raise NotImplementedError
    
    def wait_complete(self, timeout):
        '''
        Implements interface: :func:`detector.interface.IData.wait_complete()`
        '''
        raise NotImplementedError
### End of implemetation of the IData interface ###


class PercivalUI(object):
    '''
    classdocs
    '''
    exposure= 1
    control = CarrierBoard()
    data = MezzanineBoard()

    def __init__(self):
        '''
        Constructor
        '''
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        
    def acquire(self, exposure, nframes=1, whatnot = 2):
        '''
        Start the detector acquiring data
        '''
        raise NotImplementedError

# Register the classes as implementing the relevant interfaces
IControl.register(CarrierBoard)
IDetector.register(PercivalUI)
IData.register(MezzanineBoard)

# Sanity check: ensure the classes fully implement the interfaces
assert issubclass(CarrierBoard, IControl)
assert issubclass(MezzanineBoard, IData)
assert issubclass(PercivalUI, IDetector)
