#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""Implementation of Ros3D device controller REST API"""

from __future__ import absolute_import
from tornado.escape import json_encode, json_decode
import logging

from ros3ddevcontroller.param import parameter

_log = logging.getLogger(__name__)

class ParameterCodecError(Exception):
    """Parameter codec error wrapper"""
    pass

class ParameterCodec(object):
    def __init__(self, as_set=False):
        self.as_set = as_set

    @staticmethod
    def status_as_dict(status):
        """Convert ParameterStatus to JSON serializable dict"""
        assert isinstance(status, parameter.ParameterStatus)
        return {
            'read': bool(status.read),
            'write': bool(status.write),
            'status': str(status.status)
        }

    @staticmethod
    def parameter_to_dict(param):
        """Convert Parameter to JSON serializable dict"""
        ad = {
            "value": param.value,
            "type": param.value_type.__name__,
            "status": ParameterCodec.status_as_dict(param.status),
        }

        if param.min_value is not None:
            ad["minValue"] = param.min_value
        if param.max_value is not None:
            ad["maxValue"] = param.max_value

        return ad


    def encode(self, param):
        """Encode parameter to REST API representation"""
        if not self.as_set:
            raise NotImplementedError('single parameter encoder not supported')

        if not isinstance(param, list):
            param_list = [param]
        else:
            param_list = param

        return self.encode_list(param_list)

    def encode_list(self, params):
        """Encode a list of Parameter() instances"""

        out_set = {}
        for param in params:
            assert isinstance(param, parameter.Parameter)

            as_dict = ParameterCodec.parameter_to_dict(param)
            _log.debug('as dict: %s', as_dict)
            out_set[param.name] = as_dict

        enc = json_encode(out_set)
        return enc

    def decode(self, data):
        if not self.as_set:
            raise NotImplementedError('single parameter decoder not supported')

        return self.decode_list(data)

    def decode_list(self, data):
        try:
            req = json_decode(data)
        except ValueError:
            _log.exception("failed to decode JSON")
            raise ParameterCodecError("JSON decoding error")

        if not isinstance(req, dict):
            raise ParameterCodecError('Request not an object')

        if not req.items():
            raise ParameterCodecError("No request data")

        params = []
        for param, val in req.items():
            _log.debug('validate parameter %s to %s (type: %s)', param,
                       val, type(val))

            if not isinstance(val, dict):
                raise ParameterCodecError('Incorrect \'value\' field')

            if 'value' not in val:
                raise ParameterCodecError('Missing \'value\' field')

            params.append(parameter.Parameter(param, val['value'],
                          type(val['value'])))
        return params
