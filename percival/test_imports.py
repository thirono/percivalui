'''
Created on 8 May 2015

@author: up45
'''
import unittest
from percival.detector.interface import IControl, IData, IDetector
import percival.percivalui as ui


class TestImports(unittest.TestCase):

    def testImportPercivalCarrier(self):
        """import percival.carrier"""
        import percival.carrier
        
    def testImportPercivalDetector(self):
        """import percival.detector"""
        import percival.detector
        
    def testImportPercivalPercivalUI(self):
        """import percival.percivalui; from percival.percivalui import PercivalUI"""
        import percival.percivalui
        from percival.percivalui import PercivalUI

class TestInterfaces(unittest.TestCase):
        
    def testCarrierBoardInterface(self):
        """percivalui.CarrierBoard class implements the IControl interface"""
        self.assertTrue(issubclass(ui.CarrierBoard, IControl), "CarrierBoard does not adhere to the IControl interface")

    def testMezzanineBoardInterface(self):
        """percivalui.MezzanineBoard class implements the IData interface"""
        self.assertTrue(issubclass(ui.MezzanineBoard, IData), "CarrierBoard does not adhere to the IControl interface")

    def testPercivalUIInterface(self):
        """percivalui.PercivalUI class implements the IDetector interface"""
        self.assertTrue(issubclass(ui.PercivalUI, IDetector), "CarrierBoard does not adhere to the IControl interface")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    