#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""Servo driver proxy"""
from __future__ import absolute_import

from ros3ddevcontroller.param.store import ParametersStore, SERVO_PARAMETERS
from ros3ddevcontroller.param.parameter import ParameterStatus, Infinity
from ros3ddevcontroller.bus.client import DBusClientTask
import dbus

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
        self._update_servo_parameters()
        pstatus = ParameterStatus.HARDWARE
        self._set_servo_params_status(pstatus)

    def bus_service_offline(self):
        self.logger.debug('servo offline')
        self.servo = None
        pstatus = ParameterStatus.SOFTWARE
        self._set_servo_params_status(pstatus)

    @classmethod
    def _set_servo_params_status(cls, pstatus):
        """Update status of parameters that are applied to servo"""
        for pname in SERVO_PARAMETERS:
            pdesc = ParametersStore.get(pname)
            pdesc_status = pdesc.status
            pdesc_status.set_status(pstatus)
            ParametersStore.set_status(pname, pdesc_status)

    def _setup_servo_proxy(self):
        """Setup proxy to servo service, call only whe name is resolvable"""
        if self.servo:
            return

        self.logger.debug('obtain proxy to servo')
        self.servo = self.get_proxy(self.SERVO_DBUS_PATH, self.SERVO_DBUS_INTERFACE)
        if self.servo:
            self.logger.debug('got proxy')
            # connect to value change signal
            self.servo.connect_to_signal('valueChanged', self._servo_value_changed)

    def _update_servo_parameters(self):
        """Update servo parameters after connecting"""
        if not self.servo:
            return

        for param in SERVO_PARAMETERS:
            try:
                val = self.servo.getValue(param)
                ParametersStore.set(param, val)
            except dbus.DBusException:
                self.logger.exception('failed to update parameter %s from servo',
                                      param)

    def _servo_value_changed(self, parameter, motor, limit, in_progress, value):
        """pl.ros3d.servo.valueChanged signal handler"""
        self.logger.debug('got signal for parameter %s, value: %d', parameter, value)
        value = Infinity.convert_from(value)
        ParametersStore.set(parameter, value)
        self.logger.debug('parameter value updated')

    def change_param(self, param, value):
        """Attempt to set a parameter is servo.

        :rtype: bool
        :return: True if change request was sent successfuly
        """
        self.logger.debug('change param %s to %s', param, value)
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
        self.logger.debug('apply param: %s -> %s', request.param, request.value)
        try:
            res = self.servo.setValue(request.param,
                                      request.value,
                                      timeout=ServoTask.SERVO_CALL_TIMEOUT_S)
            self.logger.debug('parameter \'%s\' -> %s set request done, result: %s ',
                              request.param, request.value, res)
        except Exception as err:
            # TODO: catch DBus exception instead of Exception
            self.logger.exception('error when setting %s -> %s:',
                                  request.param, request.value)
            return False
        else:
            return True

    def is_active(self):
        """Check if servo can be used"""
        self.logger.debug('servo active? %s', 'yes' if self.servo else 'no')
        if self.servo:
            return True
        return False
