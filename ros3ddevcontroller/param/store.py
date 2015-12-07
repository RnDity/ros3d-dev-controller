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
from ros3ddevcontroller.param.sysparams import CAMERA_PARAMETERS, SERVO_PARAMETERS
from threading import RLock
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

    # dict of parameter_name: parameter_desc, for quick lookup by
    # parameter name
    PARAMETERS = {}

    # dict of parameter_name: list(parameter_desc), the list contains
    # parameter descriptors that depend on given parameter, for
    # example: for entry 'focus_distance_mm', the list will contain
    # all descriptors that have their value depend on
    # 'focus_distance_m'
    DEPENDENCIES = {}

    # Use recursive lock, this allows for internal helpers like
    # _find_param() to have both a thin lockless wrapping or a
    # complete wrapping like get()/set(). Also, this allows for
    # parameters to be modified from change_listeners callback
    lock = RLock()
    change_listeners = ParametersStoreListener()

    @staticmethod
    def is_servo_parameter(name):
        """Test if parameter with name `name` is applicable to servo

        :param name str: parameter name
        :return: True if is a servo parameter"""
        return name in SERVO_PARAMETERS

    @staticmethod
    def is_camera_parameter(name):
        """Test if parameter with name `name` is applicable to camera

        :param name str: parameter name
        :return: True if is a camera parameter
        """
        return name in CAMERA_PARAMETERS

    @classmethod
    def is_read_only(cls, name):
        """Test if parameter with given `name` is read only

        :param name str: parameter name
        :return: True if read only"""
        pdesc = cls.get(name)
        return pdesc.is_read_only()

    @classmethod
    def load_parameters(cls, params):
        """Load parameters from list

        :param list params: list of Parameter objects
        """
        with cls.lock:
            # 1st pass, load any parameters
            for p in params:
                if p.name in cls.PARAMETERS:
                    raise RuntimeError('parameter %s defined twice' % p.name)
                cls.PARAMETERS[p.name] = p
                cls.DEPENDENCIES[p.name] = []

            # 2nd pass, setup dependencies
            for p in params:
                if not p.evaluator:
                    continue
                requires = p.evaluator.REQUIRES
                for req in requires:
                    if not cls.DEPENDENCIES.has_key(req):
                        raise RuntimeError('unknown dependency %s in evaluator for parameter %s' \
                                           % (req, p.name))
                    cls.DEPENDENCIES[req].append(p)

    @classmethod
    def clear_parameters(cls):
        """Remove all parameters"""
        with cls.lock:
            cls.PARAMETERS = {}
            cls.DEPENDENCIES = {}

    @classmethod
    def parameters_as_dict(cls):
        with cls.lock:
            params = {}
            for pname, pp in cls.PARAMETERS.items():
                params[pname] = ParameterCodec.parameter_to_dict(pp)
            return params

    @classmethod
    def _find_param(cls, name):
        """Find parameter in known parameters dict and return a
        descriptor. Acquires a lock on parameters.

        :param str name: parameter name
        :return: parameter descriptor
        """
        with cls.lock:
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
    def set(cls, name, value, notify=True, evaluate=True):
        """Set a parameter, attempts automatic conversion to proper type

        :param name str: parameter name
        :param value: parameter value
        :param notify bool: trigger parameter change notification chain
        :param evaluate bool: trigger parameter evaluation
        :rtype: bool, True if successful
        :return: True if successful
        """
        _log.debug('set parameter %s to %r', name, value)

        with cls.lock:
            _log.debug('acquired')
            pdesc = cls._find_param(name)
            pdesc.value = cls._convert(pdesc, value)
            _log.debug('set value of %s to %s', name, pdesc.value)
            if notify:
                cls.change_listeners.fire(pdesc)

            if evaluate:
                cls.evaluate_param_tree(pdesc)

        return True

    @classmethod
    def evaluate_param_tree(cls, param):
        """Evalaluate paramters that depend on `param`

        :param param Parameter: parameter descriptor
        """
        dependant_params = cls.DEPENDENCIES.get(param.name, [])
        for dep_param in dependant_params:
            cls.evaluate_single_param(dep_param)

    @classmethod
    def evaluate_single_param(cls, param):
        """Evaluate a single parameter. Effectively this method will construct
        an instance of an evaluator and call it passing required
        parameters (listed in REQUIRES property of the evaluator) as
        keywords.

        :param param Parameter: parameter descriptor

        """
        args = {}
        for pname in param.evaluator.REQUIRES:
            args[pname] = ParametersStore.get_value(pname)

        # param.value = param.evaluator()(**args)
        try:
            cls.set(param.name, param.evaluator()(**args), notify=False)
        except ArithmeticError:
            _log.exception('failed to evaluate parameter %s, args: %s',
                           param.name, args)
        except Exception:
            _log.exception('unexpected error when evaluating parameter %s with args %s',
                           param.name, args)
            raise

    @classmethod
    def set_status(cls, name, status, notify=True):
        """Set a parameter status

        :param name str: parameter name
        :param status ParameterStatus: instance of parameter status
        :param notify bool: trigger parameter change notification chain
        :return: True if successful"""
        with cls.lock:
            pdesc = cls._find_param(name)
            pdesc.status = status
            if notify:
                cls.change_listeners.fire(pdesc)

        return True

    @classmethod
    def get(cls, name):
        """Get a parameter"""

        _log.debug('get parameter %s', name)
        with cls.lock:
            pdesc = cls.PARAMETERS.get(name, None)
        if not pdesc:
            raise KeyError('parameter %s not found' % (name))

        return pdesc

    @classmethod
    def get_value(cls, name):
        """Obtain a parameter's value. Raises KeyError if parameter is not
        present.

        :rtype: that of parameter
        :return: parameter value

        """
        pdesc = cls.get(name)
        return pdesc.value

    @classmethod
    def get_parameters(cls):
        """Obtaina list of all parameters, symmetric to load_parameters() call

        :rtype: list(Parameter)
        :return: list of parmeters"""
        with cls.lock:
            return cls.PARAMETERS.values()


class ParameterLoader(object):
    """Utility class for loading up a paramteres from a set"""

    @classmethod
    def load(cls):

        from ros3ddevcontroller.param.sysparams import SYSTEM_PARAMETERS

        ParametersStore.load_parameters(SYSTEM_PARAMETERS)


class ParameterSnapshotBackend(object):
    """Backend for storing parameter snapshots. A user defined class is
    expected to inherit this one and implement save() method

    """

    def save(self, parameters):
        """Save parameters snapshot

        :param parameters list: list of Parameter entries
        :rtype int:
        :return: snapshot ID
        """
        raise NotImplementedError('{:s} needs implementation'.format(__name__))

    def load(self, snapshot_id):
        """Retrieve snapshot data

        :param snapshot_id int: ID of snapshot
        :rtype list:
        :return: list of Parameter entries"""
        raise NotImplementedError('{:s} needs implementation'.format(__name__))

    def delete(self, snapshot_id):
        """Remove snapshot of ID `snapshot_id`.

        :param snapshot_id int: ID of snapshot
        :rtype int:
        :return: ID of removed snapshot

        """
        raise NotImplementedError('{:s} needs implementation'.format(__name__))

    def delete_all(self):
        """Remove all snapshots.
        :rtype list(int):
        :return: list of removed snapshots

        """
        raise NotImplementedError('{:s} needs implementation'.format(__name__))


class ParameterSnapshotter(object):
    """Utility class for saving a snapshot of all parameters to specified
    location"""

    @classmethod
    def save(cls, backend=None):
        """Save parameter using backend `backend`

        :param backend ParameterSnapshotBackend: a ParameterSnapshotBackend instance
        :rtype int:
        :return: snapshot ID
        """
        assert backend != None

        return backend.save(ParametersStore.get_parameters())

