"""
Testing import of packages

@author: Ulrik
"""
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
