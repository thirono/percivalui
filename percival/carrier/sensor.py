'''
Created on 15 July 2016

:author: Alan Greer

A class representation for the Percival Sensor.

This class will maintain the sensor DACs, and apply using the buffer transfer
when requested.

TODO: This assumes the buffer has already been filled with values.  This
class could instead of taking the number of words, take the actual words and
fill the buffer itself.
'''
from __future__ import print_function

import logging

class SensorDac(object):
    """
    Represent a sensor DAC
    """
    def __init__(self, dac_ini):
        self._log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self._log.debug("Sensor DAC created %s", dac_ini)
        self._config = dac_ini
        self._raw_value = 0

    @property
    def name(self):
        return self._config["Channel_name"]

    @property
    def buffer_index(self):
        return self._config["Buffer_index"]

    def set_value(self, value):
        self._log.debug("DAC [%s] value set to %d", self._config["Channel_name"], value)
        self._raw_value = value

    def to_buffer_word(self):
        # Raw value is ANDed with number of bits and offset
        bit_mask = (2 ** self._config["Bit_size"]) - 1
        buffer_value = self._raw_value & bit_mask
        buffer_value = buffer_value << self._config["Bit_offset"]
        self._log.debug("Buffer value returned %d", buffer_value)
        return buffer_value


class Sensor(object):
    """
    Represent the Percival Sensor.
    """
    def __init__(self, buffer_cmd):
        """
        Constructor

        :param buffer_cmd: Percival buffer command object
        :type  buffer: SensorBufferCommand
        """
        self._log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        self._buffer_cmd = buffer_cmd
        self._dacs = {}
        self._buffer_words = {}

    @property
    def dacs(self):
        return self._dacs

    def add_dac(self, dac_ini):
        """
        Add a DAC to the sensor set.
        :param dac_ini:
        :return:
        """
        # Create the SensorDAC object from the initialisation values
        dac = SensorDac(dac_ini)
        self._log.debug("Adding DAC [%s] to sensor", dac.name)
        self._dacs[dac.name] = dac
        # Keep a list of dac names for each buffer index
        if dac.buffer_index not in self._buffer_words:
            self._buffer_words[dac.buffer_index] = []

        # Append the name to the relevant buffer index store
        self._buffer_words[dac.buffer_index].append(dac.name)

    def set_dac(self, dac_name, value):
        """
        Set a DAC value ready for writing to the hardware.
        Sensor DAC values are written by buffer transfer so must all be set prior
        to a write
        :param dac_name:
        :param value:
        :return:
        """
        self._log.debug("Setting sensor DAC [%s] value: %d", dac_name, value)
        if dac_name in self._dacs:
            self._dacs[dac_name].set_value(value)

    def _generate_dac_words(self):
        # Create the set of words ready for the buffer write command
        words = []
        for index in sorted(self._buffer_words):
            word_value = 0
            for dac_name in self._buffer_words[index]:
                word_value += self._dacs[dac_name].to_buffer_word()

            words.append(word_value)
        return words

    def apply_dac_values(self):
        # Generate the words and write to the buffer
        # Send the appropriate buffer command
        words = self._generate_dac_words()
        self._log.debug("Applying sensor DAC values: %s", words)
        self._buffer_cmd.send_dacs_setup_cmd(words)

    def send_configuration_setup_cmd(self, config):
        # We need to verify the configuration
        # This might currently be hardcoded for P2M
        # TODO Verify if this method needs to be more generic
        if 'H1' in config and 'H0' in config and 'G' in config:
            h1_values = config['H1']
            words = []
            while len(h1_values) > 9:
                words.append(self.configuration_values_to_word(h1_values[0:10]))
                h1_values = h1_values[10:]
            h0_values = h1_values + config['H0']
            while len(h0_values) > 9:
                words.append(self.configuration_values_to_word(h0_values[0:10]))
                h0_values = h0_values[10:]
            g_values = h0_values + config['G']
            while len(g_values) > 9:
                words.append(self.configuration_values_to_word(g_values[0:10]))
                g_values = g_values[10:]
            if len(g_values) > 0 and len(g_values) < 10:
                g_values = (g_values + [0] * 10)[:10]
                words.append(self.configuration_values_to_word(g_values))
            self._log.debug("Sensor configuration words: %s", words)
            self._buffer_cmd.send_configuration_setup_cmd(words)

    def configuration_values_to_word(self, values):
        self._log.debug("Combining sensor ADC values into 32 bit word")
        # Verify values has a length of 10 or less
        value = 0
        if len(values) < 11:
            for index in range(10):
                value = (value << 3) + (values[index] & 0x7)
            value = value << 2
        else:
            # We cannot combine more than 10 values, raise an error
            raise RuntimeError("Sensor configuration, >10 values used to create 32 bit word")
        return value
