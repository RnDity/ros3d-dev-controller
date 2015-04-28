#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""ParameterCodec tests"""

import unittest
import json
import logging

from ros3dkr.param.parameter import Parameter
from ros3dkr.web.codec import ParameterCodec

_log = logging.getLogger(__name__)

class CodecTestCase(unittest.TestCase):

    def test_encode_single(self):
        p = Parameter('foo', 'bar', str)

        # this should produce a valid json
        enc = ParameterCodec(as_set=True).encode(p)
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
        enc = ParameterCodec(as_set=True).encode(params)
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
        dec = ParameterCodec(as_set=True)

        params = dec.decode(single)

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
        dec = ParameterCodec(as_set=True)

        params = dec.decode(single)

        self.assertIsInstance(params, list)
        self.assertEqual(len(params), 2)

        expected = {
            'foo': 10,
            'bar': 0.5
        }

        for pdesc in params:
            self.assertTrue(pdesc.name in expected)
            self.assertEqual(pdesc.value, expected[pdesc.name])






