'''
Created on 8 May 2015

@author: up45
'''
import unittest

class TestImports(unittest.TestCase):

    def testImportPercivalCarrier(self):
        """import percival.carrier"""
        import percival.carrier
        
    def testImportPercivalDetector(self):
        """import percival.detector"""
        import percival.detector
        
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
