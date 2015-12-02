#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""System parameters wrappers"""

from __future__ import absolute_import

import unittest
import mock

from ros3ddevcontroller.param.parameter import Parameter, ReadOnlyParameter, ParameterStatus

class ParameterTestCase(unittest.TestCase):
    def test_new_no_status(self):
        par = Parameter('foo', 'bar', str)

        self.assertEqual(par.name, 'foo')
        self.assertEqual(par.value, 'bar')
        self.assertIsInstance(par.value, str)
        self.assertEqual(par.value_type, str)

        self.assertTrue(hasattr(par, 'status'))
        status = par.status
        self.assertIsInstance(status, ParameterStatus)
        self.assertEqual(status.read, True)
        self.assertEqual(status.write, True)
        self.assertEqual(status.status, ParameterStatus.HARDWARE)

    def test_new_status(self):
        st = ParameterStatus()

        par = Parameter('foo', 1, int, status=st, min_val=0, max_val=10)

        self.assertEqual(par.name, 'foo')
        self.assertEqual(par.value, 1)
        self.assertIsInstance(par.value, int)
        self.assertEqual(par.value_type, int)
        self.assertEqual(par.min_value, 0)
        self.assertEqual(par.max_value, 10)
        self.assertIs(par.status, st)

    def test_new_bad_status(self):
        self.assertRaises(AssertionError, Parameter,
                          'foo', 'bar', str, status=1)

    def test_read_only(self):
        par = Parameter('foo', 'bar', str)

        self.assertFalse(par.is_read_only())

        par = ReadOnlyParameter('foo', 'bar', str)
        self.assertTrue(par.is_read_only())
