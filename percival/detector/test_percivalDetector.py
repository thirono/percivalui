from unittest import TestCase

import os
from percival.carrier.simulator import Simulator
from percival.detector.detector import PercivalDetector


class TestPercivalDetector(TestCase):
    def setUp(self):
        self.sim = Simulator()
        self.sim.start(forever=False, blocking=False)

    def tearDown(self):
        self.sim.shutdown()

    def test_load_ini(self):
        """Createing a PercivalDetector object also runs load_ini, and setup_control methods and finally load_channels"""
        pcvl = PercivalDetector(initialise_hardware=False)


    def test_initialise_board(self):
        pcvl = PercivalDetector(initialise_hardware=True)

    def test_set_global_monitoring(self):
        pcvl = PercivalDetector(initialise_hardware=True)
        pcvl.set_global_monitoring(True)
        pcvl.set_global_monitoring(False)
        pcvl.set_global_monitoring(False)

    def test_system_command(self):
        pcvl = PercivalDetector(initialise_hardware=True)
        pcvl.system_command('no_operation')
        self.assertRaises(KeyError, pcvl.system_command, 'blah')

    def test_set_value(self):
        pcvl = PercivalDetector(initialise_hardware=True)
        pcvl.set_value('VCH1', 27)

    def test_read(self):
        pcvl = PercivalDetector(initialise_hardware=True)
        result = pcvl.read('Temperature1')
        self.assertIsInstance(result, dict)

    def test_update_status(self):
        pcvl = PercivalDetector(initialise_hardware=True)
        result = pcvl.update_status()
        self.assertIsInstance(result, dict)

