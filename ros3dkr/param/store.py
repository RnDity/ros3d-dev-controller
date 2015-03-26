#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""Utility classes for managing system parameters"""


#
# TODO:
#
# - synchronization - store accessed from multiple threads
#   simultaneously
# - move parameters definition to external file or config

from __future__ import absolute_import

import logging

_log = logging.getLogger(__name__)


class ParameterStatus(object):
    """Paramter status wrapper"""
    STATUS_TYPE_HARDWARE = 'hardware'
    STATUS_TYPE_SOFTWARE = 'software'

    def __init__(self, read=True, write=True,
                 status_type=STATUS_TYPE_HARDWARE):
        self.read = read
        self.write = write
        self.status = status_type

    def as_dict(self):
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
        return {
            "value": self.value,
            "valueType": self.value_type.__name__,
            "status:": self.status.as_dict(),
            "minValue": self.min_value,
            "maxValue": self.max_value
        }


class ParametersStore(object):
    """System parameters store"""

    PARAMETERS = {
        'focus_distance_m': Parameter('focus_distance_m', 6.0, float,
                                      ParameterStatus(), 1, 100),
        'aperture': Parameter('aperture', 30.0, float,
                              ParameterStatus(), 1, 30)
    }

    @classmethod
    def parameters_as_dict(cls):
        params = {}
        for pname, pp in cls.PARAMETERS.items():
            params[pname] = pp.as_dict()
        return params

    @classmethod
    def set(cls, name, value):
        """Set a parameter, attempts automatic conversion to proper type

        :param name str: parameter name
        :param value: parameter value
        :rtype: bool, True if successful
        :return: True if successful
        """
        _log.debug('set parameter %s to %r', name, value)
        # check if paramter is known
        pdesc = cls.PARAMETERS.get(name, None)
        if not pdesc:
            raise KeyError('parameter %s not known' % (name))

        # try converting to proper value
        try:
            cval = pdesc.value_type(value)
        except ValueError:
            raise

        pdesc.value = cval

    @classmethod
    def get(cls, name):
        """Get a parameter"""

        _log.debug('get parameter %s', name)
        pdesc = cls.PARAMETERS.get(name, None)
        if not pdesc:
            raise KeyError('parameter %s not found' % (name))

        return pdesc


