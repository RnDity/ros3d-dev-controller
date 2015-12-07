#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""System parameters wrappers"""

from __future__ import absolute_import

import math
import logging


_log = logging.getLogger(__name__)


class Infinity(object):
    """Wrapper for infinity specification"""
    # infinity is expressed as values below
    PLUS = 1e100
    MINUS = -1e100

    @classmethod
    def convert_to(cls, value):
        """Convert a float value to compatible representation. Only applied if
        input value is +/-Infinity. The output value will be clamped
        to <MINUS, PLUS> range.

        :param value float: value to convert
        :rtype: float
        :return: converted value

        """
        if not isinstance(value, float):
            value = float(value)

        if value == float('inf'):
            return cls.PLUS
        elif value == float('-inf'):
            return cls.MINUS
        return value

    @classmethod
    def convert_from(cls, value):
        """Convert a float value in compatible representation to a float

        :param value float: value to convert
        :rtype: float
        :return: converted value"""

        if not isinstance(value, float):
            value = float(value)

        if value >= cls.PLUS:
            return float('inf')
        elif value <= cls.MINUS:
            return float('-inf')
        return value


class ParameterStatus(object):
    """Paramter status wrapper"""
    HARDWARE = 'hardware'
    SOFTWARE = 'software'

    def __init__(self, read=True, write=True,
                 status_type=SOFTWARE):
        self.read = read
        self.write = write
        self.status = status_type

    def set_status(self, status):
        """Set parameter status

        :param status: one of HARDWARE, SOFTWARE"""
        if status not in [ParameterStatus.HARDWARE, ParameterStatus.SOFTWARE]:
            raise ValueError('invalid status {}'.format(status))
        self.status = status

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Parameter(object):
    """System parameter wrapper"""

    def __init__(self, name, value, value_type,
                 status=None, min_val=None, max_val=None,
                 evaluator=None):
        """Initialize a parameter

        :param str name: parameter name
        :param value: parameter value, corresponding to value_type
        :param typr value_type: type of parameter value
        :param ParameterStatus status: status info, if None, defaults to a hardware paramter
        :param min_val: minimum value
        :param max_val: maximum value
        :param evaluator Evaluator: class that will be called to evaluate the parameter
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

        self.evaluator = evaluator

    def is_read_only(self):
        return self.status.write == False

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class ReadOnlyParameter(Parameter):
    """Read only parameter wrapper"""

    def __init__(self, name, value, value_type, **kwargs):
        super(ReadOnlyParameter, self).__init__(name, value, value_type,
                                                status=ParameterStatus(write=False),
                                                **kwargs)


class Evaluator(object):
    REQUIRES = []

    """A parameter evaluator helper class. When a parameter that has this
    class as an evaluator needs to be updated, an instance of this
    class will be created and called with keyword parameters listed in
    REQUIRES property.

    """

    def __call__(self, **kwargs):
        """Calculate new value of parameter. The value of parameters that are
        required for calculating this parameter will be passed as
        keyword arguments. The evaluation engine will catch and log
        ArithmeticError exception, other exceptions are allowed to
        fall through.

        :param **kwargs dict: parameters that are required for calculating this one
        :rtype: same as parameter
        :return: new value of parameter

        """
        raise NotImplementedError('Evaluation for {} not implemented'.format(self.__class__.__name__))



