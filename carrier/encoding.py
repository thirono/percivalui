'''
Created on 4 Dec 2014

@author: Ulrik Pedersen
'''
from __future__ import unicode_literals
import struct

SINGLE_MSG_FMT = b'!HI'
NUM_BYTES_PER_MSG = 6

msg_packer = struct.Struct(SINGLE_MSG_FMT)

def encode_message(addr, word):
    encoded_msg = msg_packer.pack(addr, word)
    return encoded_msg

def encode_multi_message(start_addr, words):
    addresses = range(start_addr, start_addr + len(words))
    encoded_msg = b""
    assert len(addresses) == len(words)
    for addr, word in zip(*[addresses, words]):
        encoded_msg += encode_message(addr, word)
        
    return encoded_msg

def decode_message(msg):
    extra_bytes = len(msg)%NUM_BYTES_PER_MSG
    if (extra_bytes > 0):
        msg = msg[:-extra_bytes] # WARNING: we are chopping away some bytes here...
    num_words =  len(msg)//NUM_BYTES_PER_MSG
    fmt = b"!"
    fmt += b"HI" * num_words
    
    msg_unpacker = struct.Struct(fmt)
    addr_word_list = msg_unpacker.unpack(msg)
    
    # reshape the linear list of (addr, word, addr, word, addr, word...) into a 
    # neat [(addr,word), (addr, word) ... ] list
    addr_word_sets = zip(*[iter(addr_word_list)]*2)
    
    return addr_word_sets

