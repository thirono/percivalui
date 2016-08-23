from unittest import TestCase
from percival.detector.interface import IControl, IData, IDetector


class TestIDetector(TestCase):
    def setUp(self):
        class Detector(object):
            def acquire(self, exposure, nframes):
                raise NotImplementedError
        self.Detector = Detector

    def test_fail_adhere_to_interface(self):
        """Creating a new Detector class which does not fully implement the IDetector interface"""

        # Missing the exposure property should cause the register to fail
        IDetector.register(self.Detector)
        self.assertFalse(issubclass(self.Detector, IDetector))

        dut = self.Detector()
        self.assertFalse(isinstance(dut, IDetector))

        with self.assertRaises(NotImplementedError):
            dut.acquire(1., 1)

    def test_adhere_to_interface(self):
        """Add the missing exposure property to the self.Detector class. This should complete the IDetector interface"""
        self.Detector.exposure = 11.

        IDetector.register(self.Detector)
        self.assertTrue(issubclass(self.Detector, IDetector))

        dut = self.Detector()
        self.assertTrue(isinstance(dut, IDetector))

        with self.assertRaises(NotImplementedError):
            dut.acquire(1., 1)
        self.assertEqual(dut.exposure, 11.)
        dut.exposure = 12.
        self.assertEqual(dut.exposure, 12.)
        self.assertEqual(self.Detector.exposure, 11.)


class TestIControl(TestCase):
    def setUp(self):
        class Control(object):
            def start_acquisition(self, exposure, nframes):
                raise NotImplementedError
            def get_nframes(self):
                raise NotImplementedError
        self.Control = Control

    def test_fail_adhere_to_interface(self):
        """Creating a new Detector class which does not fully implement the IControl interface"""

        # Missing the stop_acquisition method should cause the register to fail
        IControl.register(self.Control)
        self.assertFalse(issubclass(self.Control, IControl))

        dut = self.Control()
        self.assertFalse(isinstance(dut, IControl))

        with self.assertRaises(NotImplementedError):
            dut.start_acquisition(1., 1)

    def test_adhere_to_interface(self):
        """Add the missing stop_exposure method to the self.Control class.
        This should complete the IControl interface"""
        from types import MethodType
        def stop_acquisition(self):
            raise NotImplementedError
        self.Control.stop_acquisition = MethodType(stop_acquisition, None, self.Control)

        IControl.register(self.Control)
        self.assertTrue(issubclass(self.Control, IControl))

        dut = self.Control()
        self.assertTrue(isinstance(dut, IControl))


class TestIData(TestCase):
    def setUp(self):
        class Data(object):
            datasetname = ""
            def start_capture(self, filename, nframes):
                raise NotImplementedError
            def wait_complete(self, timeout):
                raise NotImplementedError
        self.Data = Data

    def test_fail_adhere_to_interface(self):
        """Creating a new Detector class which does not fully implement the IControl interface"""

        # Missing the stop_acquisition method should cause the register to fail
        IData.register(self.Data)
        self.assertFalse(issubclass(self.Data, IData))

        dut = self.Data()
        self.assertFalse(isinstance(dut, IData))

        with self.assertRaises(NotImplementedError):
            dut.start_capture("datafile", 3)

    def test_adhere_to_interface(self):
        """Add the missing stop_exposure method to the self.Control class.
        This should complete the IControl interface"""
        self.Data.filename = "mydatafile"
        IData.register(self.Data)
        self.assertTrue(issubclass(self.Data, IData))

        dut = self.Data()
        self.assertTrue(isinstance(dut, IData))

        with self.assertRaises(NotImplementedError):
            dut.start_capture("datafile", 3)
