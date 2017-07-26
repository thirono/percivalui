import unittest
import os
from percival.carrier.configuration import find_file, ChannelParameters, BoardParameters, ControlParameters,\
    SensorConfigurationParameters
from percival.carrier.const import BoardTypes


class TestConfiguration(unittest.TestCase):
    def test_find_file(self):
        # Create a nonsense search path
        os.environ["PERCIVAL_CONFIG_DIR"] = str(":/dir1:/dir2")
        # Verify an appropriate error is raised
        with self.assertRaises(IOError):
            find_file("config/nofile.ini")

        # Create a valid search path
        os.environ["PERCIVAL_CONFIG_DIR"] = str("/tmp")
        fn = find_file("ChannelParameters.ini")
        # Verify the file is found
        self.assertEquals(fn, "/tmp/ChannelParameters.ini")


class TestChannelParameters(unittest.TestCase):
    def setUp(self):
        f = open("/tmp/ChannelParameters.ini", "w+")
        f.write("\
[Control_channel<0001>]\n\
UART_address = 10\n\
Board_type = 0\n\
Channel_name = \"\"\n\
I2C_address = 0\n\
I2C_Sub_address = 0\n\
I2C_bus_selection = 0\n\
Component_family_ID = 0\n\
Device_ID = 0\n\
Channel_ID = 0\n\
Minimum_value = 0\n\
Maximum_value = 0\n\
Default_OFF_value = 0\n\
Default_ON_value = 0\n\
Value = 0\n\
Power_status = FALSE\n\
Channel_offset = 0\n\
Channel_multiplier = 1\n\
Channel_divider = 1\n\
Channel_unit = \"\"\n\
\n\
[Control_channel<0002>]\n\
UART_address = 19\n\
Board_type = 3\n\
Channel_name = \"VCH0\"\n\
I2C_address = 84\n\
I2C_Sub_address = 0\n\
I2C_bus_selection = 0\n\
Component_family_ID = 3\n\
Device_ID = 0\n\
Channel_ID = 0\n\
Minimum_value = 0\n\
Maximum_value = 65535\n\
Default_OFF_value = 0\n\
Default_ON_value = 65535\n\
Value = 0\n\
Power_status = FALSE\n\
Channel_offset = 0\n\
Channel_multiplier = 1\n\
Channel_divider = 1\n\
Channel_unit = \"\"\n\
\n\
[Monitoring_channel<0000>]\n\
UART_address = 75\n\
Board_type = 3\n\
Channel_name = \"VCH0\"\n\
I2C_address = 25\n\
I2C_Sub_address = 0\n\
I2C_bus_selection = 2\n\
Component_family_ID = 7\n\
Device_ID = 3\n\
Channel_ID = 0\n\
Extreme_low_threshold = 0\n\
Extreme_high_threshold = 4095\n\
Low_threshold = 0\n\
High_threshold = 4095\n\
Monitoring = 255\n\
Read_frequency = 1\n\
Safety_exception_threshold = 1\n\
Minimum_value = 0\n\
Maximum_value = 0\n\
Offset = 0\n\
Multiplier = 1\n\
Divider = 1000\n\
Unit = \"V\"\n\
\n\
[Monitoring_channel<0001>]\n\
UART_address = 79\n\
Board_type = 3\n\
Channel_name = \"VCH1\"\n\
I2C_address = 25\n\
I2C_Sub_address = 1\n\
I2C_bus_selection = 2\n\
Component_family_ID = 7\n\
Device_ID = 3\n\
Channel_ID = 1\n\
Extreme_low_threshold = 0\n\
Extreme_high_threshold = 4095\n\
Low_threshold = 0\n\
High_threshold = 4095\n\
Monitoring = 255\n\
Read_frequency = 1\n\
Safety_exception_threshold = 1\n\
Minimum_value = 0\n\
Maximum_value = 0\n\
Offset = 0\n\
Multiplier = 1\n\
Divider = 1000\n\
Unit = \"V\"\n\
\n\
")

    f = open("/tmp/ChannelNONE.ini", "w+")
    f.write("")

    def test_get_channels(self):
        cp = ChannelParameters("/tmp/ChannelParameters.ini")
        cp.load_ini()
        self.assertEqual(type(cp.control_channels), list)
        self.assertEqual(type(cp.monitoring_channels), list)
        self.assertEqual(cp.control_channels_by_name("VCH0").UART_address, 19)
        self.assertEqual(cp.control_channel_name_by_index(1), "Control_channel<0001>")
        self.assertEqual(cp.monitoring_channel_name_by_id_and_board_type(1, BoardTypes.carrier), "VCH1")
        self.assertEqual(cp.monitoring_channel_by_address(79).Channel_name, "VCH1")
        self.assertEqual(str(cp), "<ChannelParameters: inifile: /tmp/ChannelParameters.ini Control channels: 2 Monitoring channels: 2>")
        cp = ChannelParameters("/tmp/ChannelNONE.ini")
        cp.load_ini()
        self.assertEqual(str(cp), "<ChannelParameters: inifile: /tmp/ChannelNONE.ini Control channels: [] Monitoring channels: []>")

    def test_config_channel_parameters(self):
        """Checking loading of the config/Channel parameters.ini file (v. 2017.01.24)"""
        cp = ChannelParameters("config/Channel parameters.ini")
        cp.load_ini()
        self.assertEqual(type(cp.control_channels), list)
        self.assertEqual(type(cp.monitoring_channels), list)
        # Channel count as per version 2017.05.05
        self.assertEqual(len(cp.control_channels), 68)
        self.assertEqual(len(cp.monitoring_channels), 105)



class TestBoardParameters(unittest.TestCase):
    def setUp(self):
        f = open("/tmp/BoardCARRIER.ini", "w+")
        f.write("\
[Board_header]\n\
Board_name = \"PercivalAdapter V2.0 (S/N: 000002)\"\n\
Board_type = 3\n\
Board_revision_number = 0\n\
\n\
[Entry_counts]\n\
Components_count = 6\n\
Devices_count = 7\n\
Control_channels_count = 14\n\
Monitoring_channels_count = 19\n\
Total_channels_count = 33\n\
\n\
")
        f = open("/tmp/BoardNONE.ini", "w+")
        f.write("")

    def test_board_parameters(self):
        bp = BoardParameters("/tmp/BoardCARRIER.ini")
        bp.load_ini()
        self.assertEquals(bp.board_name, '\"PercivalAdapter V2.0 (S/N: 000002)\"')
        self.assertEquals(bp.board_type, BoardTypes.carrier)
        self.assertEquals(bp.board_revision, 0)
        self.assertEquals(bp.control_channels_count, 14)
        self.assertEquals(bp.monitoring_channels_count, 19)

    def test_board_exceptions(self):
        bp = BoardParameters("/tmp/BoardNONE.ini")
        bp.load_ini()
        with self.assertRaises(RuntimeError):
            self.assertEquals(bp.board_name, '\"PercivalAdapter V2.0 (S/N: 000002)\"')
        with self.assertRaises(RuntimeError):
            self.assertEquals(bp.board_type, BoardTypes.carrier)
        with self.assertRaises(RuntimeError):
            self.assertEquals(bp.board_revision, 0)
        with self.assertRaises(RuntimeError):
            self.assertEquals(bp.control_channels_count, 14)
        with self.assertRaises(RuntimeError):
            self.assertEquals(bp.monitoring_channels_count, 19)


class TestControlParameters(unittest.TestCase):
    def setUp(self):
        f = open("/tmp/Percival.ini", "w+")
        f.write("\
[Control]\n\
carrier_ip = \"127.0.0.1\"\n\
\n\
[Configuration]\n\
system_settings_file = \"config/SystemSettings.ini\"\n\
download_system_settings = True\n\
chip_readout_settings_file = \"config/ChipReadoutSettings.ini\"\n\
download_chip_readout_settings = True\n\
clock_settings_file = \"config/ClockSettings.ini\"\n\
download_clock_settings = True\n\
sensor_configuration_file = \"config/SensorConfiguration.ini\"\n\
download_sensor_configuration = True\n\
sensor_calibration_file = \"config/SensorCalibration.ini\"\n\
download_sensor_calibration = True\n\
sensor_debug_file = \"config/SensorDebug.ini\"\n\
download_sensor_debug = True\n\
board_bottom_settings_file = \"config/Board BOTTOM.ini\"\n\
board_carrier_settings_file = \"config/Board CARRIER.ini\"\n\
board_left_settings_file = \"config/Board LEFT.ini\"\n\
board_plugin_settings_file = \"config/Board PLUGIN.ini\"\n\
channel_settings_file = \"config/Channel parameters.ini\"\n\
")
        f = open("/tmp/PercivalNONE.ini", "w+")
        f.write("")

    def test_control_parameters(self):
        pp = ControlParameters("/tmp/Percival.ini")
        pp.load_ini()
        self.assertEquals(pp.carrier_ip, '127.0.0.1')
        self.assertEquals(pp.system_settings_file, 'config/SystemSettings.ini')
        self.assertEquals(pp.chip_readout_settings_file, 'config/ChipReadoutSettings.ini')
        self.assertEquals(pp.clock_settings_file, 'config/ClockSettings.ini')
        self.assertEquals(pp.sensor_configuration_file, 'config/SensorConfiguration.ini')
        self.assertEquals(pp.sensor_calibration_file, 'config/SensorCalibration.ini')
        self.assertEquals(pp.sensor_debug_file, 'config/SensorDebug.ini')
        self.assertEquals(pp.board_bottom_settings_file, 'config/Board BOTTOM.ini')
        self.assertEquals(pp.board_carrier_settings_file, 'config/Board CARRIER.ini')
        self.assertEquals(pp.board_left_settings_file, 'config/Board LEFT.ini')
        self.assertEquals(pp.board_plugin_settings_file, 'config/Board PLUGIN.ini')
        self.assertEquals(pp.channel_settings_file, 'config/Channel parameters.ini')

    def test_control_exceptions(self):
        pp = ControlParameters("/tmp/PercivalNONE.ini")
        pp.load_ini()
        with self.assertRaises(RuntimeError):
            self.assertEquals(pp.carrier_ip, '127.0.0.1')


class TestSensorConfigurationParameters(unittest.TestCase):
    def setUp(self):
        self._ini_description = "[General]\nCols_<H1>=5\nCols_<H0>=4\nCols_<G>=3\n\n\
[H1]\nCol0=5\nCol1=4\nCol2=3\nCol3=2\nCol4=1\n\n\
[H0]\nCol0=1\nCol1=2\nCol2=3\nCol3=4\n\n\
[G]\nCol0=3\nCol1=2\nCol2=1\n\n"

    def test_configuration_parameters(self):
        cp = SensorConfigurationParameters(unicode(self._ini_description, "utf-8"))
        cp.load_ini()
        self.assertEqual(cp.value_map, {'H1': [5, 4, 3, 2, 1],
                         'H0': [1, 2, 3, 4],
                         'G': [3, 2, 1]})

if __name__ == '__main__':
    unittest.main()
