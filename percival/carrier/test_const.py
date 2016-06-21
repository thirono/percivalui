from __future__ import unicode_literals, absolute_import

import unittest

import percival.carrier.const as const


class TestConstants(unittest.TestCase):
    def TestUARTBlock(self):
        # Verify a valid address
        self.assertEquals(const.HEADER_SETTINGS_LEFT.is_address_valid(0x0), True)
        # Verify an invalid address
        self.assertEquals(const.HEADER_SETTINGS_CARRIER.is_address_valid(0x0), False)
