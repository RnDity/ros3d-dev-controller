#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""Implementation of Ros3D KR REST API"""

from __future__ import absolute_import

import logging
import tornado.web
from tornado.escape import json_encode, json_decode
from sparts.tasks.tornado import TornadoHTTPTask
from ros3dkr.param  import ParametersStore
from functools import wraps

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


def reqhandler(method=None):
    """Decorator for producing proper response once an API error was caught
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):

        _log.debug('request: %s', self.request)
        try:
            return method(self, *args, **kwargs)
        except APIError as err:
            _log.debug("caught method error")
            self.set_status(err.HTTP_CODE)
            resp = {
                "code": err.CODE,
                "reason": str(err)
            }
            self.write(resp)
            self.finish()

    return wrapper


class SystemVersionHandler(tornado.web.RequestHandler):
    def get(self):
        version = {
            "version": API_VERSION
        }
        _log.debug("SystemVersionHandler() Response: %s", version)
        self.write(version)


class SystemStatusHandler(tornado.web.RequestHandler):
    def get(self):
        status = { }
        _log.debug("SystemStatusHandler() Response: %s", status)
        self.write(status)


class ParametersListHandler(tornado.web.RequestHandler):
    def get(self):
        params = ParametersStore.parameters_as_dict()

        _log.debug("ParametersListHandler() Response: %s" % params)
        self.write(params)


class ParametersUpdateHandler(tornado.web.RequestHandler):
    @reqhandler
    def put(self):
        _log.debug("ParametersUpdateHandler() Request: %s", self.request)

        try:
            req = json_decode(self.request.body)
        except ValueError:
            _log.exception("failed to decode JSON")
            raise InvalidDataError("JSON decoding error")

        # record changed parameters
        changed_params = {}
        if not req.items():
            raise InvalidDataError("No request data")

        for param, val in req.items():
            _log.debug('set parameter %s to %s', param, val)
            if 'value' not in val:
                raise InvalidDataError('Missing \'value\' field')

            try:
                ParametersStore.set(param, val['value'])
            except ValueError:
                raise InvalidDataError("Incorrect value type")
            par = ParametersStore.get(param)
            changed_params[par.name] = par.as_dict()

        self.write(changed_params)


class ServosCalibrateHandler(tornado.web.RequestHandler):
    def get(self):
        _log.debug("ServosCalibrateHandler()")
        calibrateServos()
        self.write("True")


class ServosConnectedHandler(tornado.web.RequestHandler):
    def get(self):
        _log.debug("ServosCalibrateHandler()")
        isConnected = isServoConnected()
        if(isConnected == 1):
	    self.write("True")
	else:
	    self.write("False")


class WebAPITask(TornadoHTTPTask):

    def getApplicationConfig(self):
        return [
            (r"/api/system/version", SystemVersionHandler),
            (r"/api/system/status", SystemStatusHandler),
            (r"/api/parameters/list", ParametersListHandler),
            (r"/api/parameters/update", ParametersUpdateHandler),
            (r"/api/servo/calibrate", ServosCalibrateHandler),
            (r"/api/servo/connected", ServosConnectedHandler),
        ]


