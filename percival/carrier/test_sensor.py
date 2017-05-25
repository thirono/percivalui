from __future__ import unicode_literals, absolute_import

import unittest, logging
from mock import MagicMock, call
from builtins import bytes

import percival.carrier.const as const
from percival.carrier.sensor import SensorDac, Sensor


class TestSensorDACClass(unittest.TestCase):
    def setUp(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(logging.DEBUG)
        dac_ini = {"Channel_name": "test_dac_001",
                   "Buffer_index": 2,
                   "Bit_offset": 20,
                   "Bit_size": 6
                   }
        self.dac = SensorDac(dac_ini)

    def test_config(self):
        self.assertEqual("test_dac_001", self.dac.name)

    def test_set_value(self):
        self.dac.set_value(25)
        self.assertEqual(0x1900000, self.dac.to_buffer_word())

class TestSensorClass(unittest.TestCase):
    def setUp(self):
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(logging.DEBUG)
        self.buffer_cmd = MagicMock()
        self.sensor = Sensor(self.buffer_cmd)

    def test_writing_to_buffer(self):
        dac_ini = {"Channel_name": "test_dac_001",
                   "Buffer_index": 1,
                   "Bit_offset": 2,
                   "Bit_size": 6
                   }
        self.sensor.add_dac(dac_ini)
        dac_ini = {"Channel_name": "test_dac_002",
                   "Buffer_index": 1,
                   "Bit_offset": 8,
                   "Bit_size": 6
                   }
        self.sensor.add_dac(dac_ini)
        dac_ini = {"Channel_name": "test_dac_003",
                   "Buffer_index": 1,
                   "Bit_offset": 14,
                   "Bit_size": 6
                   }
        self.sensor.add_dac(dac_ini)
        dac_ini = {"Channel_name": "test_dac_004",
                   "Buffer_index": 1,
                   "Bit_offset": 20,
                   "Bit_size": 6
                   }
        self.sensor.add_dac(dac_ini)
        dac_ini = {"Channel_name": "test_dac_005",
                   "Buffer_index": 1,
                   "Bit_offset": 26,
                   "Bit_size": 6
                   }
        self.sensor.add_dac(dac_ini)
        dac_ini = {"Channel_name": "test_dac_006",
                   "Buffer_index": 2,
                   "Bit_offset": 2,
                   "Bit_size": 6
                   }
        self.sensor.add_dac(dac_ini)
        dac_ini = {"Channel_name": "test_dac_007",
                   "Buffer_index": 2,
                   "Bit_offset": 8,
                   "Bit_size": 6
                   }
        self.sensor.add_dac(dac_ini)
        dac_ini = {"Channel_name": "test_dac_008",
                   "Buffer_index": 2,
                   "Bit_offset": 14,
                   "Bit_size": 6
                   }
        self.sensor.add_dac(dac_ini)
        dac_ini = {"Channel_name": "test_dac_009",
                   "Buffer_index": 2,
                   "Bit_offset": 20,
                   "Bit_size": 6
                   }
        self.sensor.add_dac(dac_ini)
        dac_ini = {"Channel_name": "test_dac_010",
                   "Buffer_index": 2,
                   "Bit_offset": 26,
                   "Bit_size": 6
                   }
        self.sensor.add_dac(dac_ini)

        # Verify that initially all words are zero
        self.assertEqual([0x0, 0x0], self.sensor._generate_dac_words())

        # Now set the value of a DAC in the first word
        self.sensor.set_dac("test_dac_002", 24)
        # Verify that the words are correctly set
        self.assertEqual([0x1800, 0x0], self.sensor._generate_dac_words())

        # Set another value in the first word
        self.sensor.set_dac("test_dac_004", 61)
        # Verify that the words are correctly set
        self.assertEqual([0x3D01800, 0x0], self.sensor._generate_dac_words())

        # Set a value in the second word
        self.sensor.set_dac("test_dac_008", 13)
        # Verify that the words are correctly set
        self.assertEqual([0x3D01800, 0x34000], self.sensor._generate_dac_words())

        # Set a value in the second word
        self.sensor.set_dac("test_dac_006", 49)
        # Verify that the words are correctly set
        self.assertEqual([0x3D01800, 0x340C4], self.sensor._generate_dac_words())

        # Execute the send_setup_to_dac command
        self.buffer_cmd.reset()
        self.buffer_cmd.send_dacs_setup_cmd = MagicMock()
        self.sensor.apply_dac_values()
        self.buffer_cmd.send_dacs_setup_cmd.assert_called_with([0x3D01800, 0x340C4])
