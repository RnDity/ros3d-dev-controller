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

from ros3ddevcontroller.param.parameter import Parameter
from ros3ddevcontroller.web.codec import ParameterCodec

import logging


_log = logging.getLogger(__name__)

class ParametersStoreListener(object):
    """Class for notifying other modules about any changes in parameters"""

    def __init__(self):
        self.__handlers = []

    def add(self, handler):
        if handler not in self.__handlers:
            _log.debug('registering %r handler', handler)
            self.__handlers.append(handler)
        else:
            _log.warning('handler %r already registered', handler)

    def remove(self, handler):
        try:
            self.__handlers.remove(handler)
        except ValueError:
            _log.warning('handler %r was not registered', handler)

    def fire(self, *args, **keywargs):
        for handler in self.__handlers:
            _log.debug('callling %r', handler)
            handler(*args, **keywargs)


class ParametersStore(object):
    """System parameters store"""

    PARAMETERS = {}

    change_listeners = ParametersStoreListener()

    @classmethod
    def load_parameters(cls, params):
        """Load parameters from list

        :param list params: list of Parameter objects
        """

        for p in params:
            assert p.name not in cls.PARAMETERS
            cls.PARAMETERS[p.name] = p

    @classmethod
    def clear_parameters(cls):
        """Remove all parameters"""
        cls.PARAMETERS = {}

    @classmethod
    def parameters_as_dict(cls):
        params = {}
        for pname, pp in cls.PARAMETERS.items():
            params[pname] = ParameterCodec.parameter_to_dict(pp)
        return params

    @classmethod
    def _find_param(cls, name):
        """Find parameter in known parameters dict and return a descriptor

        :param str name: parameter name
        :return: parameter descriptor
        """
        # check if paramter is known
        pdesc = cls.PARAMETERS.get(name, None)
        if not pdesc:
            raise KeyError('parameter %s not known' % (name))
        return pdesc

    @classmethod
    def _convert(cls, pdesc, value):
        """Convert a parameter value according to descriptor. Will throw
        `ValueError` if conversion fails.

        :param pdesc: parameter descriptor
        :param value: parameter value
        :return: converted value
        """
        # try converting to proper value
        try:
            cval = pdesc.value_type(value)
        except ValueError:
            raise
        return cval

    @classmethod
    def validate(cls, name, value):
        """Validate that parameter is of correct value

        :param name str: parameter name
        :param value: parameter value
        :throws ValueError: if parameter failed to validate
        """
        pdesc = cls._find_param(name)
        # attempt conversion
        cls._convert(pdesc, value)

    @classmethod
    def validate_desc(cls, desc):
        """Validate that parameter passed as Parameter instance has correct
        value. Aside from same exceptions as validate(), also throws
        an AssertError.

        :throws AssertError: desc is not a Parameter() instance
        """
        assert isinstance(desc, Parameter)
        pdesc = cls._find_param(desc.name)
        # attempt conversion
        cls._convert(pdesc, desc.value)

    @classmethod
    def set(cls, name, value):
        """Set a parameter, attempts automatic conversion to proper type

        :param name str: parameter name
        :param value: parameter value
        :rtype: bool, True if successful
        :return: True if successful
        """
        _log.debug('set parameter %s to %r', name, value)

        pdesc = cls._find_param(name)
        pdesc.value = cls._convert(pdesc, value)
        cls.change_listeners.fire(pdesc)
        return True

    @classmethod
    def get(cls, name):
        """Get a parameter"""

        _log.debug('get parameter %s', name)
        pdesc = cls.PARAMETERS.get(name, None)
        if not pdesc:
            raise KeyError('parameter %s not found' % (name))

        return pdesc


class ParameterLoader(object):
    """Utility class for loading up a paramteres from a set"""

    @classmethod
    def load(cls):

        from ros3ddevcontroller.param.sysparams import SYSTEM_PARAMETERS

        ParametersStore.load_parameters(SYSTEM_PARAMETERS)
