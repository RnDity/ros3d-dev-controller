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
"""Core Ros3D controller logic"""
from __future__ import absolute_import
import logging
import datetime
from ros3ddevcontroller.param.store import ParametersStore, ParameterSnapshotter
from ros3ddevcontroller.param.backends import FileSnapshotBackend
from ros3ddevcontroller.bus import servo
from ros3ddevcontroller.util import make_dir
from threading import Lock

class Controller(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.servo = None
        self.camera = None
        self.snapshots_location = None
        self.snapshots_backend = None
        self.lock = Lock()

    def set_servo(self, servo):
        """Servo interface"""
        self.logger.debug('setting servo to %s', servo)
        self.servo = servo

    def set_camera(self, camera):
        self.logger.debug('setting camera to %s', camera)
        self.camera = camera

    def set_snapshots_location(self, loc):
        """Set location of snapshots"""
        self.snapshots_location = loc
        make_dir(self.snapshots_location)

        # update snapshots backend
        self.snapshots_backend = FileSnapshotBackend(self.snapshots_location)

    @classmethod
    def is_servo_parameter(cls, param):
        """Return true if parameter is applicable to servo"""
        return ParametersStore.is_servo_parameter(param.name)

    def apply_servo_parameter(self, param):
        """Apply parameter to servo

        :param param Parameter: parameter to apply
        :rtype: bool
        :return: True if successful"""
        value = param.value
        name = param.name
        self.logger.debug('set servo param')
        try:
            if self.servo.is_active():
                res = self.servo.change_param(name, value)
                self.logger.debug('apply result: %s', res)
                return res
            else:
                return self.apply_other_parameter(param)
        except servo.ParamApplyError:
            self.logger.exception('error when applying a parameter')
            return False

    @classmethod
    def is_camera_parameter(cls, param):
        """Return True if parameter is applicable to camera"""
        return ParametersStore.is_camera_parameter(param.name)

    def apply_camera_parameter(self, param):
        """Apply camera parameter

        :param param Parameter: parameter to apply
        :rtype: bool
        :return: True if successful"""
        value, name = param.value, param.name

        try:
            if self.camera.is_active():
                res = self.camera.set_param(name, value)
                self.logger.debug('apply result: %s', res)
                return res
            else:
                return self.apply_other_parameter(param)
        except Exception:
            self.logger.exception('unexpected error when setting camera parameter')
            return False

    @classmethod
    def is_parameter_writable(cls, param):
        """Return True if parameter is applicable to camera"""
        return ParametersStore.is_read_only(param.name) == False

    def apply_other_parameter(self, param):
        """Apply parameter directly in parameter store, i.e. skipping any
        interaction with external devices.

        :param param Parameter:
        :rtype: bool
        :return: True"""
        value = param.value
        name = param.name
        ParametersStore.set(name, value)
        return True

    def apply_single_parameter(self, param):
        """Apply single parameter

        :param param Parameter: parameter descriptor"""
        if not self.is_parameter_writable(param):
            self.logger.warning('parameter %s is read-only, skipping', param.name)
            status = False
        elif self.is_servo_parameter(param):
            status = self.apply_servo_parameter(param)
        elif self.is_camera_parameter(param):
            status = self.apply_camera_parameter(param)
        else:
            status = self.apply_other_parameter(param)
        return status

    def apply_parameters(self, params):
        """Apply a parameter set

        :param params list of ParamDesc: list of parameters to apply
        :rtype: list(Parameter)
        :return: list of parameters applied"""
        # record changed parameter descriptors
        changed_params = []

        # apply parameters serially, note that if any parameter takes
        # longer to aplly this will contribute to wait time of the
        # whole request
        for param in params:
            applied = self.apply_single_parameter(param)

            # param validation was successful and was applied to servo
            if applied:
                par = ParametersStore.get(param.name)
                changed_params.append(par)

        return changed_params

    def get_parameters(self):
        """Return a dict with all parameters in the system"""
        return ParametersStore.parameters_as_dict()

    def _record_timestamp(self):
        """Helper for updating current timestamp in parameters"""
        now = datetime.datetime.now()
        ParametersStore.set('record_date', now.strftime('%Y-%m-%d'),
                            notify=False)
        ParametersStore.set('record_time', now.strftime('%H:%M:%S'),
                            notify=False)

    def take_snapshot(self):
        """Record a snapshot of current parameter set
        :return: ID of snapshot
        """
        with self.lock:
            # record timestamp
            self._record_timestamp()

            return ParameterSnapshotter.save(self.snapshots_backend)

    def list_snapshots(self):
        """List IDs of available snapshots

        :rtype list(int):
        :return: list of snapshot IDs
        """
        with self.lock:
            snapshots = self.snapshots_backend.list_snapshots()
            self.logger.debug('snapshots: %s', snapshots)
            return snapshots

    def get_snapshot(self, snapshot_id):
        """Obtain data of snapshot `snapshot_id`. Returns a dictionary with
        parameters stored in the snapshot

        :param snapshot_id int: ID of snapshot
        :rtype dict:

        """
        with self.lock:
            self.logger.debug('load snapshot %d', snapshot_id)
            sdata = self.snapshots_backend.load(snapshot_id)
            if not sdata:
                self.logger.error('failed to load snapshot data for ID %d', snapshot_id)
            return sdata

    def delete_snapshot(self, snapshot_id):
        """Remove snapshot snapshot `snapshot_id`.

        :param snapshot_id int: ID of snapshot
        :return: ID of removed snapshot

        """
        with self.lock:
            self.logger.debug('delete snapshot %d', snapshot_id)
            return self.snapshots_backend.delete(snapshot_id)

    def delete_all(self):
        """Remove all snapshots.

        :return: list of removed snapshot IDs

        """
        with self.lock:
            return self.snapshots_backend.delete_all()
