#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""Servo driver proxy"""
from __future__ import absolute_import

from sparts.tasks.dbus import DBusTask
from sparts.sparts import option
from concurrent.futures import Future
import glib
import logging
import dbus

_log = logging.getLogger(__name__)


class ParamApplyRequest(object):
    """Wrapper for keeping a parameter apply request in check"""
    def __init__(self, param, value):
        self.future = Future()
        self.param = param
        self.value = value


class ParamApplyError(Exception):
    """Error wrapper class"""
    pass


class ServoTask(DBusTask):
    """Servo driver proxy. The proxy will automatically find a DBus servo
    service and connect to it.

    Since the task is running in a Glib MainLoop possibly on a
    different thread than the caller of `change_param()` method, a
    trampoline is used. The request is wrapped into
    `ParamApplyRequest` and `change_param()` returns a `Future()`
    object.
    """

    OPT_PREFIX = 'dbus'

    SERVO_DBUS_SERVICE = 'pl.ros3d.servo'
    SERVO_DBUS_PATH = '/pl/ros3d/servo'

    session_bus = option(action='store_true', type=bool,
        default=False, help='Use session bus')

    def start(self):
        """Start task. Perform necessary setup:
        - bus connection
        - setup servo service name monitoring
        - obtain proxy to servo if possible
        """
        _log.debug('starting servo task for service: %s', self.service.name)
        # get bus
        if self.session_bus:
            _log.info('using session bus')
            self.bus = dbus.SessionBus(private=True)
        else:
            self.bus = dbus.SystemBus(private=True)

        # proxy to servo service
        self.servo = None

        if self.bus.name_has_owner(ServoTask.SERVO_DBUS_SERVICE):
            _log.debug('servo module already present, grab proxy')
            self._setup_servo_proxy()

        # we're monitoring servo name changes
        self.bus.watch_name_owner(ServoTask.SERVO_DBUS_SERVICE,
                                  self._servo_name_changed)

        super(ServoTask, self).start()

    def stop(self):
        """Stop task"""
        # get rid of reference to bus
        self.bus = None

        super(ServoTask, self).stop()

    def _servo_name_changed(self, name):
        """Callback for when a name owner of servo service has changed

        :param str name: service name, either actual servo name or empty
        """

        _log.debug('servo name changed: %s', name)

        if not name:
            _log.info('servo driver lost')
            self.servo = None
        else:
            self._setup_servo_proxy()

    def _setup_servo_proxy(self):
        """Setup proxy to servo service, call only whe name is resolvable"""
        if self.servo:
            return

        _log.debug('obtain proxy to servo')
        try:
            self.servo = self.bus.get_object(ServoTask.SERVO_DBUS_SERVICE,
                                             ServoTask.SERVO_DBUS_PATH)
        except dbus.DBusException:
            _log.exception('failed to obtain proxy to servo')
        else:
            _log.debug('got proxy')
            # connect to value change signal
            self.servo.connect_to_signal('valueChanged', self._servo_value_changed)

    def _servo_value_changed(self, parameter, motor, limit, in_progress, value):
        """pl.ros3d.servo.valueChanged signal handler"""
        _log.debug('got signal for parameter %s, value: %d', parameter, value)

    def change_param(self, param, value):
        """Attempt to set a parameter is servo. Does a trampoline through the
        main loop. Returns a Future(), that the caller should wait for
        to get a result.

        :rtype: concurrent.futures.Future()
        """
        _log.debug('change param %s to %s', param, value)
        pa = ParamApplyRequest(param, value)
        glib.idle_add(self._apply_param, pa)
        return pa.future

    def _apply_param(self, request):
        """Apply parameter. This is called in glib main loop idle
        callback. Once the parameter has been applied, it will set the
        Future() within `request` object to a result or an exception.

        :param ParamApply request: request object
        """
        _log.debug('apply param: %s -> %s', request.param, request.value)
        future = request.future
        # servo proxy might have gone away before we reached this
        # callback
        if not self.servo:
            _log.debug('no servo at this time, request fails')
            future.set_result(False)
            return

        try:
            res = self.servo.setValue(request.param,
                                      request.value)
            _log.debug('parameter \'%s\' -> %s set request done, result: %s ',
                       request.param, request.value, res)
            # setValue has signature 'by'
            future.set_result(res[0])
        except dbus.DBusException:
            _log.exception('error when setting %s -> %s',
                           request.param, request.value)
            future.set_exception(ParamApplyError('failed to apply parameter'))

    def is_active(self):
        """Check if servo can be used"""
        _log.debug('servo active?')
        if self.servo:
            return True
        return False
