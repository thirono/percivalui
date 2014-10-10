'''
The main PercivalUI module

'''
try:
    import pkg_resources
    pkg_resources.require('numpy')
    pkg_resources.require('h5py')
except:
    pass

import numpy as np
import h5py

import time
import logging
logger = logging.getLogger(__name__)

import detector.parameter
from detector.interface import IDetector, IControl, IData

class PercivalSimulator:
    # This is a singleton
    __instance = None
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(PercivalSimulator, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self):
        self.log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self.data = None
        self.file = None
        
    def create_data(self, dims, dtype=np.uint16):
        self.log.debug("creating some data with dtype: %s" % dtype)
        rand = np.random.random(dims)
        if np.issubdtype(dtype, np.float):
            factor = 1.0
        elif np.issubdtype(dtype, np.integer):
            factor = np.iinfo(dtype).max
        else:
            raise TypeError
        self.data = np.array(factor * rand, dtype=dtype)
        self.log.debug("Created data: %s" % self.data)
        
    def store_data(self, file_name, dataset_name):
        self.log.debug("file_name = %s, dataset_name = %s" % (file_name, dataset_name))
        self.log.debug("Data: %s"%str(self.data))
        f = h5py.File(file_name, 'w')
        try:
            f.create_dataset(dataset_name, data = self.data)
        finally:
            f.close()
        
        
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
    #### End IControl interface implementation ####        

    def initialise_fpga(self):
        raise NotImplementedError



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
    def set_datasetname(self, value):
        self._datasetname = str(value)
    datasetname = property(get_datasetname, set_datasetname)

    def start_capture(self, filename, nframes):
        '''
        Implements interface: :func:`detector.interface.IData.start_capture()`
        '''
        sim = PercivalSimulator()
        sim.create_data([100,100])

        self.filename = filename
        self.datasetname = 'data'
        sim.store_data(self.filename, self.datasetname)
    
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
