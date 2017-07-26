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

    def test_values_to_data_word(self):
        # Verify the combining of configuration values for ADCs which are operational
        test_values = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.assertEqual(self.sensor.configuration_values_to_word(3, test_values), 0)
        test_values = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.assertEqual(self.sensor.configuration_values_to_word(3, test_values), 613566756)
        test_values = [1, 2, 3, 4, 5, 6, 7, 0, 1, 2]
        self.assertEqual(self.sensor.configuration_values_to_word(3, test_values), 701216808)

        # Verify too many values will generate an exception
        with self.assertRaises(RuntimeError):
            test_values = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            self.sensor.configuration_values_to_word(3, test_values)

        # Try 6 bit values
        test_values = [0, 0, 0, 0, 0]
        self.assertEqual(self.sensor.configuration_values_to_word(6, test_values), 0)
        test_values = [1, 1, 1, 1, 1]
        self.assertEqual(self.sensor.configuration_values_to_word(6, test_values), 68174084)

        # Verify too many values will generate an exception
        with self.assertRaises(RuntimeError):
            test_values = [1, 1, 1, 1, 1, 1]
            self.sensor.configuration_values_to_word(6, test_values)

    def test_apply_configuration(self):
        self.buffer_cmd.send_configuration_setup_cmd = MagicMock()
        test_config = {
            'H1': [0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 2,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 3,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 4,
                   0, 0, 0, 0, 5],
            'H0': [0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 2,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 3,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 4,
                   0, 0, 5],
            'G': [0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 2,
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 3,
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 4,
                  0, 0, 0, 0, 5]
        }
        self.sensor.apply_configuration(test_config)
        # Verify that the buffer command was called with the correct words
        self.buffer_cmd.send_configuration_setup_cmd.assert_called_with([0x04,
                                                                         0x08,
                                                                         0x0C,
                                                                         0x10,
                                                                         0xA0000,
                                                                         0x20000,
                                                                         0x40000,
                                                                         0x60000,
                                                                         0x80500,
                                                                         0x100,
                                                                         0x200,
                                                                         0x300,
                                                                         0x400,
                                                                         0x2800000])

    def test_apply_debug(self):
        self.buffer_cmd.send_debug_setup_cmd = MagicMock()
        test_debug = {
            'H1': [0, 0, 0, 0, 1,
                   0, 0, 0, 0, 2,
                   0, 0, 0, 0, 3,
                   0, 0, 0, 0, 4,
                   0, 5],
            'H0': [0, 0, 0, 0, 1,
                   0, 0, 0, 0, 2,
                   0, 0, 0, 0, 3,
                   0, 0, 0, 0, 4,
                   0, 5],
            'G': [1]
        }
        self.sensor.apply_debug(test_debug)
        # Verify that the buffer command was called with the correct words
        self.buffer_cmd.send_debug_setup_cmd.assert_called_with([0x04,
                                                                 0x08,
                                                                 0x0C,
                                                                 0x10,
                                                                 0x500000,
                                                                 0x100000,
                                                                 0x200000,
                                                                 0x300000,
                                                                 0x400504])

    def test_combine_9bit_lists_into_8bit_list(self):
        test_list_1 = [1,1,1,1]
        test_list_2 = [1,1,1,1]
        self.assertEqual(self.sensor.combine_9bit_lists_into_8bit_list(test_list_1, test_list_2),
                         [0, 128, 64, 32, 16, 8, 4, 2, 1])

        test_list_1 = [1, 2, 3, 4]
        test_list_2 = [5, 6, 7, 8]
        self.assertEqual(self.sensor.combine_9bit_lists_into_8bit_list(test_list_1, test_list_2),
                         [0, 129, 64, 64, 96, 24, 28, 8, 8])

    def test_combine_8bit_lists_into_32bit_list(self):
        test_list_1 = [1, 2, 3, 4]
        test_list_2 = [5, 6, 7, 8]
        test_list_3 = [9, 10, 11, 12]
        test_list_4 = [13, 14, 15, 16]
        self.assertEqual(self.sensor.combine_8bit_lists_into_32bit_list(test_list_1,
                                                                        test_list_2,
                                                                        test_list_3,
                                                                        test_list_4),
                         [17107213, 33950222, 50793231, 67636240])

    def test_apply_calibration(self):
        self.buffer_cmd.send_calibration_setup_cmd = MagicMock()
        test_calibration = {'H1':{'Cal1': {'Right': [1, 2, 3, 4],
                                           'Left': [5, 6, 7, 8]},
                                  'Cal2': {'Right': [9, 10, 11, 12],
                                           'Left': [13, 14, 15, 16]},
                                  'Cal3': {'Right': [17, 18, 19, 20],
                                           'Left': [21, 22, 23, 24]},
                                  'Cal4': {'Right': [25, 26, 27, 28],
                                           'Left': [29, 30, 31, 32]},
                                  },
                            'H0': {'Cal1': {'Right': [33, 34, 35, 36],
                                            'Left': [37, 38, 39, 40]},
                                   'Cal2': {'Right': [41, 42, 43, 44],
                                            'Left': [45, 46, 47, 48]},
                                   'Cal3': {'Right': [49, 50, 51, 52],
                                            'Left': [53, 54, 55, 56]},
                                   'Cal4': {'Right': [57, 58, 59, 60],
                                            'Left': [61, 62, 63, 64]},
                                   },
                            'G':  {'Cal1': {'Right': [65, 66, 67, 68],
                                            'Left': [69, 70, 71, 72]},
                                   'Cal2': {'Right': [73, 74, 75, 76],
                                            'Left': [77, 78, 79, 80]},
                                   'Cal3': {'Right': [81, 82, 83, 84],
                                            'Left': [85, 86, 87, 88]},
                                   'Cal4': {'Right': [89, 90, 91, 92],
                                            'Left': [93, 94, 95, 96]},
                                   }
                            }
        self.sensor.apply_calibration(test_calibration)

        self.buffer_cmd.send_calibration_setup_cmd.assert_called_with([0x0004080C,
                                                                       0x81838587,
                                                                       0x40414243,
                                                                       0x40404141,
                                                                       0x60E060E0,
                                                                       0x185898D8,
                                                                       0x1C3C5C7C,
                                                                       0x08182838,
                                                                       0x08101820,
                                                                       0x1014181C,
                                                                       0x898B8D8F,
                                                                       0x44454647,
                                                                       0x42424343,
                                                                       0x61E161E1,
                                                                       0x185898D8,
                                                                       0x9CBCDCFC,
                                                                       0x48586878,
                                                                       0x28303840,
                                                                       0x2024282C,
                                                                       0x91939597,
                                                                       0x48494A4B,
                                                                       0x44444545,
                                                                       0x62E262E2,
                                                                       0x195999D9,
                                                                       0x1C3C5C7C,
                                                                       0x8898A8B8,
                                                                       0x48505860])

