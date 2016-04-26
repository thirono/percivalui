import unittest

from percival.configuration import ChannelParameters


class TestChannelParameters(unittest.TestCase):
    def test_get_channels(self):
        cp = ChannelParameters("config/Channel parameters.ini")
        cp.load_ini()
        self.assertEqual(type(cp.control_channels), list)
        self.assertEqual(type(cp.monitoring_channels), list)


if __name__ == '__main__':
    unittest.main()
