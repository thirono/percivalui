'''
The main PercivalUI module

'''

import time
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

    #### IControl interface implementation ####        
    def start_acquisition(self, exposure, nframes):
        #raise NotImplementedError
        pass
    
    def stop_acquisition(self):
        #raise NotImplementedError
        pass
    
    def get_nframes(self):
        #raise NotImplementedError
        return 42

    def powerup_sequence(self):
        raise NotImplementedError
    #### End IControl interface implementation ####        



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
        pass
    
    def wait_complete(self, timeout):
        '''
        Implements interface: :func:`detector.interface.IData.wait_complete()`
        '''
        # TODO: implement proper wait for file saving complete. For the moment we just sleep
        sleepfor = 1.0 if timeout is None else timeout
        time.sleep(sleepfor)
        
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
        
    def acquire(self, exposure, nframes=1, wait=True):
        '''
        Start the detector acquiring data
        '''
        self.control.start_acquisition(exposure, nframes)
        if wait:
            # Cait until acquisition is complete.
            # Calculate a suitable timeout based on exposure time and number of frames
            # TODO: for the moment we just fake it with a bit of a sleep here
            time.sleep(exposure * nframes)
        nframes_acq = self.control.get_nframes()
        return nframes_acq

# Register the classes as implementing the relevant interfaces
IControl.register(CarrierBoard)
IDetector.register(PercivalUI)
IData.register(MezzanineBoard)

# Sanity check: ensure the classes fully implement the interfaces
assert issubclass(CarrierBoard, IControl)
assert issubclass(MezzanineBoard, IData)
assert issubclass(PercivalUI, IDetector)
