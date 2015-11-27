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


class Parameter(object):
    """System parameter wrapper"""

    def __init__(self, name, value, value_type,
                 status=None, min_val=None, max_val=None,
                 evaluated=False, evaluator=None):
        """Initialize a parameter

        :param str name: parameter name
        :param value: parameter value, corresponding to value_type
        :param typr value_type: type of parameter value
        :param ParameterStatus status: status info, if None, defaults to a hardware paramter
        :param min_val: minimum value
        :param max_val: maximum value
        :param evaluated: True if value is evaluated
        :param evaluator: Class that will be called to evaluate the parameter
        """
        self.name = name
        self.value = value
        self.value_type = value_type

        if not status:
            self.status = ParameterStatus(read=True, write=True,
                                          status_type=ParameterStatus.SOFTWARE)
        else:
            assert isinstance(status, ParameterStatus)
            self.status = status

        self.min_value = min_val
        self.max_value = max_val

        self.evaluated = evaluated
        self.evaluator = evaluator


class Evaluator(object):
    NAME = 'unset'

    def __call__(self):
        raise NotImplementedError('Evaluation for {} not implemented'.format(self.__name__))
