'''
Created on 25 Jul 2014

@author: up45
'''
from detector.interface import IDetector, IControl, IData

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


p = PercivalUI()

assert isinstance(p, IDetector)

assert hasattr(p, 'acquire')
