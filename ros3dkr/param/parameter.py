#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""System parameters wrappers"""

from __future__ import absolute_import

import logging

_log = logging.getLogger(__name__)


class ParameterStatus(object):
    """Paramter status wrapper"""
    HARDWARE = 'hardware'
    SOFTWARE = 'software'

    def __init__(self, read=True, write=True,
                 status_type=HARDWARE):
        self.read = read
        self.write = write
        self.status = status_type

    def as_dict(self):
        """Return a JSON serializable dict"""
        return {
            'read': bool(self.read),
            'write': bool(self.write),
            'status': str(self.status)
        }


class Parameter(object):
    """System parameter wrapper"""

    def __init__(self, name, value, value_type,
                 status, min_val, max_val):
        self.name = name
        self.value = value
        self.value_type = value_type
        self.status = status
        self.min_value = min_val
        self.max_value = max_val

    def as_dict(self):
        """Return a JSON serializable dict"""
        return {
            "value": self.value,
            "valueType": self.value_type.__name__,
            "status:": self.status.as_dict(),
            "minValue": self.min_value,
            "maxValue": self.max_value
        }

