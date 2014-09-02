'''
The main PercivalUI module

'''

import logging
logger = logging.getLogger(__name__)

from detector.interface import IDetector, IControl, IData, IParameter

class DAC(IParameter):
    def __init__(self, v):
        self.fpga_register = None
    def convert_to_dac(self):
        return self.value

class CarrierBoard(object):
    pass

class MezzanineBoard(object):
    pass


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
IParameter.register(DAC)

# Sanity check: ensure the classes fully implement the interfaces
assert issubclass(CarrierBoard, IControl)
assert issubclass(MezzanineBoard, IData)
assert issubclass(PercivalUI, IDetector)
assert issubclass(DAC, IParameter)


p = PercivalUI()

assert isinstance(p, IDetector)

assert hasattr(p, 'acquire')
