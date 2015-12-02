#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""Implementation of Ros3D device controller REST API"""

from __future__ import absolute_import

import logging
import tornado.web
from tornado.escape import json_decode, json_encode
from sparts.tasks.tornado import TornadoHTTPTask
from tornado import gen
from ros3ddevcontroller.param  import ParametersStore
from ros3ddevcontroller.bus.servo import ServoTask, ParamApplyError
from ros3ddevcontroller.web.codec import ParameterCodec, ParameterCodecError


_log = logging.getLogger(__name__)

# REST API version
API_VERSION = '1.0'

class APIError(Exception):
    """General API Error wrapper"""
    ERROR_PERMISSION_DENIED = 1
    ERROR_INVALID_DATA = 2
    ERROR_NOT_IMPLEMENTED = 3
    ERROR_REQUEST_FAILED = 4
    ERROR_RESOURCE_DOES_NOT_EXIST = 5

    CODE = ERROR_NOT_IMPLEMENTED
    HTTP_CODE = 500


class PermissionDeniedError(APIError):
    """Permission denied when executing a request"""
    CODE = APIError.ERROR_PERMISSION_DENIED
    HTTP_CODE = 401


class InvalidDataError(APIError):
    """Request contains invalid or incomplete data"""
    CODE = APIError.ERROR_INVALID_DATA
    HTTP_CODE = 400


class RequestFailedError(APIError):
    """Permission denied when executing a request"""
    CODE = APIError.ERROR_REQUEST_FAILED
    HTTP_CODE = 500


class TaskRequestHandler(tornado.web.RequestHandler):
    """Helper class for setting up a request handler. Fields from
    parameter dictionary passed as `arg` will be added to class
    fields

    """
    def initialize(self, **kwargs):
        """Implement intialze callback. Append keyword args to class fields"""
        for k, v in kwargs.items():
            setattr(self, k, v)

    def _respond_with_error(self, err):
        """Respond with error
        :param APIError error: exception that has been thrown"""
        _log.exception("caught method error")
        self.set_status(err.HTTP_CODE)
        resp = {
            "code": err.CODE,
            "reason": str(err)
        }
        self.write(resp)
        self.finish()


class SystemVersionHandler(TaskRequestHandler):
    def get(self):
        version = {
            "version": API_VERSION
        }
        _log.debug("SystemVersionHandler() Response: %s", version)
        self.write(version)


class SystemStatusHandler(TaskRequestHandler):
    def get(self):
        status = {}
        _log.debug("SystemStatusHandler() Response: %s", status)
        self.write(status)


class ParametersListHandler(TaskRequestHandler):
    def get(self):
        params = self.task.controller.get_params()

        _log.debug("ParametersListHandler() Response: %s" % params)
        self.write(params)


class ParametersUpdateHandler(TaskRequestHandler):
    def _validate_request(self, data):
        """Parse and validate request data

        :return: validated dict with request data
        """
        try:
            req = ParameterCodec(as_set=True).decode(data)
        except ParameterCodecError as perr:
            raise InvalidDataError(str(perr))

        for param in req:
            try:
                ParametersStore.validate_desc(param)
            except ValueError:
                _log.exception('failed to validate parameter %s', param.name)
                raise InvalidDataError("Incorrect value type of parameter %s" % (param.name))

        return req

    @gen.coroutine
    def _apply_parameters(self, req):
        """Apply parameters that came in request

        :param dict req: dictionary with parameters found in request
        :return: dict of changed parameters with their values
        """
        # record changed parameters
        changed_params = []

        # apply parameters serially, note that if any parameter takes
        # longer to aplly this will contribute to wait time of the
        # whole request
        for param in req:
            servo = self.task.get_servo()
            value = param.value
            name = param.name
            try:
                if servo and servo.is_active():
                    applied = yield self.apply_param(name, value)
                else:
                    applied = True
            except ParamApplyError:
                applied = False

            # param validation was successful and was applied to servo
            if applied:
                ParametersStore.set(name, value)
            else:
                raise RequestFailedError('Failed to apply parameter %s' % (name))
            par = ParametersStore.get(name)
            changed_params.append(par)

        raise gen.Return(changed_params)

    @gen.coroutine
    def apply_param(self, param, value):
        """Apply a single parameter

        :return: Future with result"""
        _log.debug('set servo param')
        try:
            res = yield self.task.get_servo().change_param(param, value)
            _log.debug('apply result: %s', res)
        except ParamApplyError:
            _log.exception('error when applying a parameter')
            res = False
        raise gen.Return(res)

    @gen.coroutine
    def put(self):
        _log.debug("ParametersUpdateHandler() Request: %s", self.request)

        try:
            req = self._validate_request(self.request.body)
            changed_params = yield self._apply_parameters(req)
            self.write(ParameterCodec(as_set=True).encode(changed_params))

        except APIError as err:
            self._respond_with_error(err)


class SnapshotsCaptureHandler(TaskRequestHandler):
    def post(self):
        _log.debug("SnapshotsCaptureHandler() Request: %s", self.request)

        try:
            snapshot_id = self.task.controller.take_snapshot()
            self.write(json_encode([snapshot_id]))
        except APIError as err:
            self._respond_with_error(err)


class SnapshotsListHandler(TaskRequestHandler):
    def get(self):
        _log.debug("SnapshotsListHandler() Request: %s", self.request)

        try:
            snapshots = self.task.controller.list_snapshots()
            self.write(json_encode(snapshots))
        except APIError as err:
            self._respond_with_error(err)

    def delete(self):
        _log.debug("SnapshotsListHandler() Request: %s", self.request)
        try:
            deleted_snapshots = self.task.controller.delete_all()
            self.write(json_encode(deleted_snapshots))
        except APIError as err:
            self._respond_with_error(err)



class SnapshotHandler(TaskRequestHandler):
    def get(self, snapshot_id):
        _log.debug("SnapshotsGetHandler() Request: %s", self.request)

        try:
            sid = int(snapshot_id)
            _log.debug("get snapshot: %d", sid)

            snapshot = self.task.controller.get_snapshot(sid)
            self.write(ParameterCodec(as_set=True).encode(snapshot))
        except APIError as err:
            self._respond_with_error(err)

    def delete(self, snapshot_id):
        _log.debug("SnapshotsGetHandler() Request: %s", self.request)

        try:
            sid = int(snapshot_id)
            _log.debug("get snapshot: %d", sid)

            deleted_sid = self.task.controller.delete_snapshot(sid)
            self.write(json_encode([deleted_sid]))
        except APIError as err:
            self._respond_with_error(err)



class ServosCalibrateHandler(TaskRequestHandler):
    def get(self):
        _log.debug("ServosCalibrateHandler()")
        self._respond_with_error(RequestFailedError('Not implemented'))


class ServosConnectedHandler(TaskRequestHandler):
    def get(self):
        _log.debug("ServosCalibrateHandler()")
        self._respond_with_error(RequestFailedError('Not implemented'))


class WebAPITask(TornadoHTTPTask):
    DEFAULT_PORT = 8090

    def getApplicationConfig(self):
        return [
            (r"/api/system/version", SystemVersionHandler, dict(task=self)),
            (r"/api/system/status", SystemStatusHandler, dict(task=self)),
            (r"/api/parameters/list", ParametersListHandler, dict(task=self)),
            (r"/api/parameters/update", ParametersUpdateHandler, dict(task=self)),
            (r"/api/snapshots/list", SnapshotsListHandler, dict(task=self)),
            (r"/api/snapshots/capture", SnapshotsCaptureHandler, dict(task=self)),
            (r"/api/snapshots/(\d)", SnapshotHandler, dict(task=self)),
            (r"/api/servo/calibrate", ServosCalibrateHandler, dict(task=self)),
            (r"/api/servo/connected", ServosConnectedHandler, dict(task=self)),
        ]

    def start(self):
        """Override start method to take reference to servo task."""
        super(WebAPITask, self).start()

        _log.debug("API task starting")

        self.servo_task = self.service.controller.servo
        _log.debug('servo task: %s', self.servo_task)

    def get_servo(self):
        """Access servo task"""
        return self.servo_task

    @property
    def controller(self):
        """Access controller instance"""
        return self.service.controller

