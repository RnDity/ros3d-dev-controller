#
# Copyright (c) 2015 Open-RnD Sp. z o.o.
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use, copy,
# modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""ParameterCodec tests"""
from __future__ import absolute_import, print_function
import unittest
import os.path

from ros3ddevcontroller.controller import Controller
from ros3ddevcontroller.param.store import ParametersStore
from ros3ddevcontroller.param.parameter import Parameter, ReadOnlyParameter


class ControllerTestCase(unittest.TestCase):
    # list of Parameters for loading
    PARAMETERS = []
    # helper dict, key = parameter name, value = Parameter instance
    PARAMETERS_DICT = {}

    def setUp(self):
        ParametersStore.load_parameters(self.PARAMETERS)
        for param in self.PARAMETERS:
            self.PARAMETERS_DICT[param.name] = param

        self.ctrl = Controller()

    def tearDown(self):
        ParametersStore.clear_parameters()


class ParmetersGetTestCase(ControllerTestCase):
    PARAMETERS = [
        Parameter('foo-writable', 'bar', str),
        ReadOnlyParameter('foo-readonly', 'baz', str)
    ]

    def test_get(self):
        dict_params = self.ctrl.get_parameters()

        for param in self.PARAMETERS:
            self.assertTrue(dict_params.has_key(param.name))

        self.assertFalse(dict_params.has_key('foo-not-present'))


class ParametersApplyTestCase(ControllerTestCase):
    PARAMETERS = [
        Parameter('foo-writable', 'bar', str),
        ReadOnlyParameter('foo-readonly', 'baz', str)
    ]

    def test_apply(self):

        to_apply = [
            Parameter('foo-writable', 'test', str),
            Parameter('foo-readonly', 'test2', str)
        ]

        applied = self.ctrl.apply_parameters(to_apply)
        # only one parameter was applied
        self.assertEqual(len(applied), 1)
        app_param = applied[0]
        self.assertEqual(app_param.name, 'foo-writable')
        self.assertEqual(app_param.value, 'test')

        # writable parameter was set
        self.assertEqual(ParametersStore.get('foo-writable').value, 'test')
        # readonly remains unchanged
        self.assertEqual(ParametersStore.get('foo-readonly').value, 'baz')


class SnapshotsSetupTestCase(ControllerTestCase):
    def test_snapshots_location(self):

        import tempfile
        # use mktemp() to get a name of file that did not exist
        tmpdir = tempfile.mktemp()

        self.assertFalse(os.path.exists(tmpdir))
        self.ctrl.set_snapshots_location(tmpdir)
        self.assertTrue(os.path.exists(tmpdir))

        import shutil
        shutil.rmtree(tmpdir)


class SnapshotTestCaseBase(ControllerTestCase):
    """Helper for test caeses that use controller and snapshots. The class
    sets up location for storing snapshots"""
    SNAPSHOTS_LOCATION = None

    def setUp(self):
        super(SnapshotTestCaseBase, self).setUp()

        # temporary snapshots location
        import tempfile
        self.SNAPSHOTS_LOCATION = tempfile.mkdtemp()
        self.ctrl.set_snapshots_location(self.SNAPSHOTS_LOCATION)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.SNAPSHOTS_LOCATION)

        super(SnapshotTestCaseBase, self).tearDown()


class SnapshotsTestCase(SnapshotTestCaseBase):
    PARAMETERS = [
        Parameter('foo-writable', 'bar', str),
        ReadOnlyParameter('foo-readonly', 'baz', str),
        # snapshot records a timestamp in record_date parameter
        ReadOnlyParameter('record_date', '', str)
    ]

    def test_take_snapshot(self):

        # there should be no files in snapshots directory
        self.assertEqual(os.listdir(self.SNAPSHOTS_LOCATION), [])

        self.ctrl.take_snapshot()

        # there snould be some files in the snapshots directory
        self.assertNotEqual(os.listdir(self.SNAPSHOTS_LOCATION), [])

        snaps = self.ctrl.list_snapshots()
        self.assertEqual(len(snaps), 1)

        # get a snapshot of current parameters list
        snap = self.ctrl.get_snapshot(snaps[0])

        self.assertEqual(len(snap), len(self.PARAMETERS))
        self.assertTrue(isinstance(snap, list))

        # make sure that all parameters are found in the snapshot and
        # that they have correct values
        all_params = [p.name for p in self.PARAMETERS]
        for param in snap:
            self.assertTrue(isinstance(param, Parameter))
            all_params.remove(param.name)

            # parameters that went into the snapshot
            self.assertTrue(self.PARAMETERS_DICT.has_key(param.name))
            in_param = self.PARAMETERS_DICT[param.name]
            self.assertEqual(in_param.name, param.name)
            self.assertEqual(in_param.value, param.value)

        self.assertEqual(all_params, [])

    def test_modify_take_snapshot(self):

        # take snapshot with current parameters
        self.ctrl.take_snapshot()

        snaps = self.ctrl.list_snapshots()
        self.assertEqual(len(snaps), 1)

        for param in snaps:
            if param == 'foo-writable':
                self.assertEqual(param.value, 'bar')

        # now modify a value of foo-writable and take another snapshot
        self.ctrl.apply_parameters([Parameter('foo-writable', 'test', str)])
        self.ctrl.take_snapshot()

        snaps = self.ctrl.list_snapshots()

        self.assertEqual(len(snaps), 2)

        # most recent snapshot gets the highest snapshot ID
        last_snap = max(snaps)

        snap = self.ctrl.get_snapshot(last_snap)

        for param in snap:
            if param.name == 'foo-writable':
                self.assertEqual(param.value, 'test')
