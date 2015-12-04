#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""Servo driver proxy"""
from __future__ import absolute_import

from ros3ddevcontroller.param.store import ParametersStore, SERVO_PARAMETERS
from ros3ddevcontroller.param.parameter import ParameterStatus, Infinity
from ros3ddevcontroller.bus.client import DBusClientTask
import logging
import dbus

_log = logging.getLogger(__name__)


class ParamApplyRequest(object):
    """Wrapper for keeping a parameter apply request in check

    :ivar param str: parameter name
    :ivar value: parameter value"""
    def __init__(self, param, value):
        self.param = param
        self.value = value


class ParamApplyError(Exception):
    """Error wrapper class"""
    pass


class ServoTask(DBusClientTask):
    """Servo driver proxy. The proxy will automatically find a DBus servo
    service and connect to it.
    """
    OPT_PREFIX = 'servo-dbus'

    DBUS_SERVICE_NAME = 'pl.ros3d.servo'
    SERVO_DBUS_PATH = '/pl/ros3d/servo'
    SERVO_DBUS_INTERFACE = "pl.ros3d.servo"
    SERVO_CALL_TIMEOUT_S = 120 # seconds

    def __init__(self, *args, **kwargs):
        super(ServoTask, self).__init__(*args, **kwargs)

        self.servo = None

    def bus_service_online(self):
        self.logger.debug('servo online')
        self._setup_servo_proxy()
        pstatus = ParameterStatus.HARDWARE
        self._set_servo_params_status(pstatus)

    def bus_service_offline(self):
        self.logger.debug('servo offline')
        self.servo = None
        pstatus = ParameterStatus.SOFTWARE
        self._set_servo_params_status(pstatus)

    @classmethod
    def _set_servo_params_status(cls, pstatus):
        for pname in SERVO_PARAMETERS:
            pdesc = ParametersStore.get(pname)
            pdesc_status = pdesc.status
            pdesc_status.set_status(pstatus)
            ParametersStore.set_status(pname, pdesc_status)

    def _setup_servo_proxy(self):
        """Setup proxy to servo service, call only whe name is resolvable"""
        if self.servo:
            return

        _log.debug('obtain proxy to servo')
        try:
            servo_obj = self.bus.get_object(self.DBUS_SERVICE_NAME,
                                            self.SERVO_DBUS_PATH)
            self.servo = dbus.Interface(servo_obj,
                                        self.SERVO_DBUS_INTERFACE)
        except dbus.DBusException:
            _log.exception('failed to obtain proxy to servo')
        else:
            _log.debug('got proxy')
            # connect to value change signal
            self.servo.connect_to_signal('valueChanged', self._servo_value_changed)

    def _servo_value_changed(self, parameter, motor, limit, in_progress, value):
        """pl.ros3d.servo.valueChanged signal handler"""
        _log.debug('got signal for parameter %s, value: %d', parameter, value)
        value = Infinity.convert_from(value)
        ParametersStore.set(parameter, value)
        _log.debug('parameter value updated')

    def change_param(self, param, value):
        """Attempt to set a parameter is servo.

        :rtype: bool
        :return: True if change request was sent successfuly
        """
        _log.debug('change param %s to %s', param, value)
        value = Infinity.convert_to(value)
        pa = ParamApplyRequest(param, value)
        return self._apply_param(pa)

    def _apply_param(self, request):
        """Apply parameter to servo. Does not wait for servo to finish the
        operation.

        :param ParamApply request: request object
        :rtype: bool
        :return: True if parameter was sent to servo

        """
        _log.debug('apply param: %s -> %s', request.param, request.value)
        try:
            res = self.servo.setValue(request.param,
                                      request.value,
                                      timeout=ServoTask.SERVO_CALL_TIMEOUT_S)
            _log.debug('parameter \'%s\' -> %s set request done, result: %s ',
                       request.param, request.value, res)
        except Exception as err:
            # TODO: catch DBus exception instead of Exception
            _log.exception('error when setting %s -> %s:',
                           request.param, request.value)
            return False
        else:
            return True

    def is_active(self):
        """Check if servo can be used"""
        _log.debug('servo active? %s', 'yes' if self.servo else 'no')
        if self.servo:
            return True
        return False
