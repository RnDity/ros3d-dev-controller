#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""ParameterCodec tests"""

import unittest
import mock

from ros3ddevcontroller.param.store import ParametersStore, ParameterLoader
from ros3ddevcontroller.param.parameter import Parameter, ReadOnlyParameter

class StoreLoadingTestCase(unittest.TestCase):
    def setUp(self):
        ParameterLoader.load()

    def tearDown(self):
        ParametersStore.clear_parameters()


class GetSetStoreTestCase(StoreLoadingTestCase):

    def test_get_existing(self):
        from ros3ddevcontroller.param.sysparams import SYSTEM_PARAMETERS

        for param in SYSTEM_PARAMETERS:
            name = param.name
            value = param.value

            try:
                from_store = ParametersStore.get(param.name)
            except KeyError:
                self.fail('Expecting key in the set')

            self.assertEqual(name, from_store.name)
            self.assertEqual(value, from_store.value)
            self.assertEqual(param.value_type, from_store.value_type)

    def test_get_missing(self):

        self.assertRaises(KeyError,
                          ParametersStore.get, 'non-existent-param')
        self.assertRaises(KeyError,
                          ParametersStore.get, '')
        self.assertRaises(KeyError,
                          ParametersStore.get, None)


    def test_set(self):
        # test that a parameter can be set
        test_param = 'focus_distance_m'
        test_val = 10.0

        self.assertTrue(ParametersStore.set(test_param, test_val))
        focus_set = ParametersStore.get(test_param)

        self.assertEqual(focus_set.value, test_val)

    def test_set_convert(self):
        # test that parameter can be set, and the value is
        # automatically converted to proper type
        test_param = 'focus_distance_m'
        test_val = 10
        expecting_type = float

        # test value is an int
        self.assertIsInstance(test_val, int)

        # first read it
        param = ParametersStore.get(test_param)
        self.assertEqual(param.value_type, expecting_type)
        self.assertIsInstance(param.value, expecting_type)

        # set
        ParametersStore.set(test_param, test_val)
        as_set = ParametersStore.get(test_param)
        # the type should have been converted according to parameter
        # description
        self.assertIsInstance(as_set.value, expecting_type)
        self.assertEqual(as_set.value, expecting_type(test_val))

    def test_set_validate_failed(self):
        # test setting of parameter where the automatic conversion fails
        # set

        test_param = 'focus_distance_m'
        test_val = 'foo'
        expecting_type = float

        # this will raise ValueError obviously
        self.assertRaises(ValueError, expecting_type, test_val)

        focus_before = ParametersStore.get(test_param)

        # same as this one
        self.assertRaises(ValueError, ParametersStore.set,
                          test_param, test_val)
        self.assertRaises(ValueError, ParametersStore.validate,
                          test_param, test_val)
        self.assertRaises(KeyError, ParametersStore.validate,
                          test_param + '=foo', test_val)
        self.assertRaises(KeyError, ParametersStore.set,
                          test_param + '=foo', test_val)

        # try to fetch the parameter again to compare that its value
        # is unchaged
        focus_after = ParametersStore.get(test_param)

        self.assertIs(focus_before, focus_after)

    def test_validate_pdesc_failed(self):
        # test setting of parameter where the automatic conversion fails
        # set

        test_param = 'focus_distance_m'
        test_val = 'foo'
        expecting_type = float

        param = Parameter(test_param, test_val, expecting_type)

        # we know the parameter, this should not raise anything
        ParametersStore.get(test_param)

        # same as this one
        self.assertRaises(ValueError, ParametersStore.set,
                          param.name, param.value)
        self.assertRaises(ValueError, ParametersStore.validate,
                          param.name, param.value)
        self.assertRaises(ValueError, ParametersStore.validate_desc,
                          param)

        # change value to correct one
        param.value = 10
        try:
            ParametersStore.validate_desc(param)
        except Exception as err:
            self.fail("Exception raised")

    def test_validate_not_pdesc_failed(self):
        param = 1

        # param is not Parameter(), this should fail
        self.assertRaises(AssertionError, ParametersStore.validate_desc,
                          param)


class ListenerTestCase(StoreLoadingTestCase):
    def test_called(self):
        # verify that a callback was called only once for each set
        tmock = mock.Mock()

        test_param = 'focus_distance_m'
        test_value = 10.0

        # register mock callback a couple of times, only one
        # registration is used
        ParametersStore.change_listeners.add(tmock)
        ParametersStore.change_listeners.add(tmock)
        ParametersStore.change_listeners.add(tmock)

        # set a parameter
        ParametersStore.set(test_param, test_value)

        # has to be called
        self.assertTrue(tmock.called)
        # called only once
        self.assertEquals(tmock.call_count, 1)
        self.assertEquals(len(tmock.call_args), 2)
        # grab the first list parameter
        pdesc = tmock.call_args[0][0]
        self.assertIsInstance(pdesc, Parameter)
        self.assertEquals(pdesc.name, test_param)
        self.assertEquals(pdesc.value, test_value)

        # set once again
        ParametersStore.set(test_param, test_value + 1)
        self.assertEquals(tmock.call_count, 2)
        # grab the first list parameter
        pdesc = tmock.call_args[0][0]
        self.assertEquals(pdesc.value, test_value + 1)

        # remove callback
        ParametersStore.change_listeners.remove(tmock)
        # and again, should not fail
        ParametersStore.change_listeners.remove(tmock)
        # now something different
        ParametersStore.change_listeners.remove(None)


class CameraServoTestCase(StoreLoadingTestCase):

    def setUp(self):
        super(CameraServoTestCase, self).setUp()
        from ros3ddevcontroller.param.sysparams import SERVO_PARAMETERS, CAMERA_PARAMETERS
        self.servo_parameters = SERVO_PARAMETERS
        self.camera_parameters = CAMERA_PARAMETERS

    def test_servo(self):

        for p in self.servo_parameters:
            self.assertTrue(ParametersStore.is_servo_parameter(p))
        for p in self.camera_parameters:
            self.assertFalse(ParametersStore.is_servo_parameter(p))

    def test_camera(self):

        for p in self.camera_parameters:
            self.assertTrue(ParametersStore.is_camera_parameter(p))
        for p in self.servo_parameters:
            self.assertFalse(ParametersStore.is_camera_parameter(p))


class ReadOnlyParameterTestCase(unittest.TestCase):

    def setUp(self):

        ParametersStore.load_parameters([
            ReadOnlyParameter('foo-readonly', 'bar', str),
            Parameter('foo-writable', 'bar', str)
        ])

    def test_parameter_readonly(self):

        self.assertTrue(ParametersStore.is_read_only('foo-readonly'))
        self.assertFalse(ParametersStore.is_read_only('foo-writable'))


class ParameterGetValueTestCase(unittest.TestCase):
    PARAMETERS = [
            Parameter('foo', 1, int),
            Parameter('bar', 'baz', str)
    ]

    def setUp(self):
        ParametersStore.load_parameters(self.PARAMETERS)

    def tearDown(self):
        ParametersStore.clear_parameters()

    def find_key_param(self, name):
        found = [pdesc for pdesc in self.PARAMETERS
                 if pdesc.name == name]
        return found[0]

    def test_get_value(self):

        for param_in in self.PARAMETERS:
            pdesc = ParametersStore.get(param_in.name)
            self.assertEqual(param_in.name, pdesc.name)
            self.assertEqual(param_in.value, pdesc.value)
            self.assertEqual(param_in.value_type, pdesc.value_type)

            pvalue = ParametersStore.get_value(param_in.name)
            self.assertEqual(pvalue, param_in.value)
            self.assertEqual(type(pvalue), param_in.value_type)

