"""
Percival detector errors and exceptions
"""

from exceptions import Exception


class PercivalCommsError(Exception):
    pass


class PercivalProtocolError(Exception):
    pass
