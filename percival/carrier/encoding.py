'''
Created on 4 Dec 2014

@author: Ulrik Pedersen
'''
from __future__ import unicode_literals, absolute_import
from builtins import bytes
try:
    import itertools.izip as zip
except ImportError:
    pass

import struct
import logging
logger = logging.getLogger(__name__)

SINGLE_MSG_FMT = b'!HI'
NUM_BYTES_PER_MSG = 6
DATA_ENCODING='latin-1' # Just because latin-1 allow values from 0-255

msg_packer = struct.Struct(SINGLE_MSG_FMT)

def encode_message(addr, word):
    logger.debug("%s"%([addr, word]))
    encoded_msg = msg_packer.pack(addr, word)
    # Python 2 -> 3 compatibility workaround:
    # In python2 struct.pack() returns a string which we then
    # need to convert to a 'bytes' object.
    if isinstance(encoded_msg, str):
        encoded_msg = bytes( encoded_msg, encoding=DATA_ENCODING)
    logger.debug("returning: %s"%[encoded_msg])
    return encoded_msg

def encode_multi_message(start_addr, words):
    logger.debug("%s"%([start_addr, words]))
    addresses = range(start_addr, start_addr + len(words))
    encoded_msg = bytes("", encoding=DATA_ENCODING)
    assert len(addresses) == len(words)
    for addr, word in zip(*[addresses, words]):
        encoded_msg += encode_message(addr, word)
    logger.debug("returning: %s"%[encoded_msg])
    return encoded_msg

def decode_message(msg):
    logger.debug(msg)
    extra_bytes = len(msg)%NUM_BYTES_PER_MSG
    if (extra_bytes > 0):
        logger.warning("Too many (%d) bytes in message"%extra_bytes)
        msg = msg[:-extra_bytes] # WARNING: we are chopping away some bytes here...
    num_words =  len(msg)//NUM_BYTES_PER_MSG
    fmt = b"!"
    fmt += b"HI" * num_words
    
    msg_unpacker = struct.Struct(fmt)
    addr_word_list = msg_unpacker.unpack(msg)
    
    # reshape the linear list of (addr, word, addr, word, addr, word...) into a 
    # neat [(addr,word), (addr, word) ... ] list
    addr_word_sets = [ aw_set for aw_set in zip(*[iter(addr_word_list)]*2) ]
    logger.debug("Returning: %s"%str(addr_word_sets))
    return addr_word_sets

