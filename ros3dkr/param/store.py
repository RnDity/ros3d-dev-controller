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
import sys
from ros3dkr.param.parameter import Parameter, ParameterStatus

_log = logging.getLogger(__name__)


class ParametersStore(object):
    """System parameters store"""

    PARAMETERS = {
        'focus_distance_m' : Parameter('focus_distance_m', 5.0, float),
        'aperture'         : Parameter('aperture', 30.0, float),
        'focal_length_mm'  : Parameter('focal_length_mm', 35, float),
        'convergence_deg'  : Parameter('convergence_deg', 0.026, float),
        'baseline_mm'      : Parameter('baseline_mm', 80, float)
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


