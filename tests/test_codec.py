#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""ParameterCodec tests"""

import unittest
import json
import logging

from ros3ddevcontroller.param.parameter import Parameter, Infinity
from ros3ddevcontroller.web.codec import ParameterCodec, ParameterCodecError

_log = logging.getLogger(__name__)

class CodecTestCase(unittest.TestCase):

    def setUp(self):
        self.codec = ParameterCodec(as_set=True)

    def test_encode_single(self):
        p = Parameter('foo', 'bar', str)

        # this should produce a valid json
        enc = self.codec.encode(p)
        _log.debug('encoded: %s', enc)

        try:
            parsed = json.loads(enc)
        except ValueError:
            self.fail('invalid JSON produced')

        _log.debug('parsed: %s', parsed)
        self.assertIsInstance(parsed, dict)
        self.assertTrue('foo' in parsed)
        self.assertTrue('value' in parsed['foo'])
        self.assertTrue('type' in parsed['foo'])
        self.assertTrue('status' in parsed['foo'])
        self.assertEqual(parsed['foo']['value'], 'bar')
        self.assertEqual(parsed['foo']['type'], str.__name__)

    def test_encode_no_set(self):
        p = Parameter('foo', 'bar', str)

        # this should produce a valid json
        codec = ParameterCodec()
        self.assertRaises(NotImplementedError, codec.encode, p)

    def test_encode_list(self):
        params = [
            Parameter('foo', 'bar', str),
            Parameter('baz', 1, int)
        ]

        # this should produce a valid json
        enc = self.codec.encode(params)
        _log.debug('encoded: %s', enc)

        try:
            parsed = json.loads(enc)
        except ValueError:
            self.fail('invalid JSON produced')

        _log.debug('parsed: %s', parsed)
        self.assertIsInstance(parsed, dict)
        self.assertTrue('foo' in parsed)
        self.assertTrue('baz' in parsed)

    def test_decode_single(self):
        single = '''{
        "foo": {
            "value": 10
        }
        }'''
        params = self.codec.decode(single)

        self.assertIsInstance(params, list)
        self.assertEqual(len(params), 1)

        pdesc = params[0]
        self.assertEqual(pdesc.name, 'foo')
        self.assertEqual(pdesc.value, 10)

    def test_decode_many(self):
        single = '''{
        "foo": {
            "value": 10
        },
        "bar": {
            "value": 0.5
        }
        }'''

        params = self.codec.decode(single)

        self.assertIsInstance(params, list)
        self.assertEqual(len(params), 2)

        expected = {
            'foo': 10,
            'bar': 0.5
        }

        for pdesc in params:
            self.assertTrue(pdesc.name in expected)
            self.assertEqual(pdesc.value, expected[pdesc.name])

    def test_decode_fail_empty_object(self):
        # pass JSON with emtpy object to decoder
        single = '''{
        }'''

        self.assertRaises(ParameterCodecError, self.codec.decode,
                          single)

    def test_decode_fail_empty(self):
        # pass invalid JSON to decoder
        single = ''

        self.assertRaises(ParameterCodecError, self.codec.decode,
                          single)

    def test_decode_fail_param_empty(self):
        # pass invalid JSON to decoder
        single = '''{
            "foo": {}
        }'''

        self.assertRaises(ParameterCodecError, self.codec.decode,
                          single)

    def test_decode_fail_param_not_dict(self):
        # pass invalid JSON to decoder
        single = '''{
            "foo": []
        }'''

        self.assertRaises(ParameterCodecError, self.codec.decode,
                          single)

    def test_encode_infinity(self):
        params = [
            Parameter('foo-max', float('inf'), float),
            Parameter('foo-min', float('-inf'), float),
            Parameter('foo-other', 20e10, float)
        ]

        encoded = self.codec.encode(params)

        _log.debug('encoded: %s', encoded)
        dec = json.loads(encoded)
        _log.debug('parsed: %s', dec)


        self.assertEqual(dec['foo-max']['value'], Infinity.PLUS)
        self.assertEqual(dec['foo-min']['value'], Infinity.MINUS)
        self.assertEqual(dec['foo-other']['value'], 20e10)

    @staticmethod
    def find_param_in_list(params_list, name):
        """Helper for locating parameter of name `name` in list of Parameter
        instances

        :param params_list list(Parameter):
        :param name str: parameter name
        :rtype: Paramter
        :return: found instance of parameter"""
        for p in params_list:
            if p.name == name:
                return p
        raise AssertionError('parameter %s not present' % name)

    def test_decode_infinity(self):
        js = '''{
        "foo-max": {
            "value": 1e100
        },
        "foo-min": {
            "value": -1e100
        },
        "foo-other": {
            "value": 20e10
        },
        "foo-too-max": {
            "value": 20e100
        },
        "foo-too-min": {
            "value": -20e100
        }
        }'''

        params = self.codec.decode(js)

        foo_max = CodecTestCase.find_param_in_list(params, 'foo-max')
        self.assertEqual(foo_max.value, float('inf'))

        foo_min = CodecTestCase.find_param_in_list(params, 'foo-min')
        self.assertEqual(foo_min.value, float('-inf'))

        foo_other = CodecTestCase.find_param_in_list(params, 'foo-other')
        self.assertEqual(foo_other.value, 20e10)

        foo_too_max = CodecTestCase.find_param_in_list(params, 'foo-too-max')
        self.assertEqual(foo_too_max.value, float('inf'))

        foo_too_min = CodecTestCase.find_param_in_list(params, 'foo-too-min')
        self.assertEqual(foo_too_min.value, float('-inf'))
