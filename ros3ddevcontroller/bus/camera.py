#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""Camera Controller wrapper"""
from __future__ import absolute_import
from ros3ddevcontroller.bus.client import DBusClientTask
from ros3ddevcontroller.param.store import ParametersStore, CAMERA_PARAMETERS
from ros3ddevcontroller.param.parameter import ParameterStatus
from datetime import datetime
import glib
import dbus

class CameraTask(DBusClientTask):
    """Camera Controller proxy
    """
    OPT_PREFIX = 'camera-controller'

    DBUS_SERVICE_NAME = 'org.ros3d.CameraController'
    DBUS_OBJECT_PATH = '/org/ros3d/controller'
    DBUS_INTERFACE_NAME = "org.ros3d.CameraController"
    CAMERA_DBUS_INTERFACE = "org.ros3d.Camera"

    DISCOVERY_TIMEOUT = 10

    CAMERA_STATE_INACTIVE = 0
    CAMERA_STATE_ACTIVE_STOPPED = 1
    CAMERA_STATE_ACTIVE_RECORDING = 2

    # states that should trigger a snapshot of parameters, each is a
    # tuple of (current state, previous state)
    SNAPSHOT_STATES = [
        (CAMERA_STATE_ACTIVE_STOPPED, CAMERA_STATE_ACTIVE_RECORDING),
        (CAMERA_STATE_ACTIVE_RECORDING, CAMERA_STATE_ACTIVE_STOPPED)
    ]

    def __init__(self, *args, **kwargs):
        super(CameraTask, self).__init__(*args, **kwargs)

        self.camctl = None
        self.active_cams = []
        self.last_discovery = None
        self.camera_state = self.CAMERA_STATE_INACTIVE

    def start(self):
        super(CameraTask, self).start()

    def bus_service_online(self):
        self.logger.debug('camera controller service available')
        self._set_camera_status(ParameterStatus.SOFTWARE)
        self._setup_camctl_proxy()

    def _set_camera_status(self, pstatus):
        for pname in CAMERA_PARAMETERS:
            pdesc = ParametersStore.get(pname)
            pdesc_status = pdesc.status
            pdesc_status.set_status(pstatus)
            ParametersStore.set_status(pname, pdesc_status)

    def _setup_camera(self, cam_path):
        """Setup camera handling"""

        # skip if camera is already known
        if self._is_camera_active(cam_path):
            return

        cam = self.get_proxy(cam_path, self.CAMERA_DBUS_INTERFACE)
        if cam:
            cam.connect_to_signal('stateChanged', self._camera_state_changed)
            cam.connect_to_signal('valueChanged', self._camera_parameter_changed)
            # add camera to list of used cameras so that a reference
            # is kept around
            self.active_cams.append(cam)

            # update state
            self.camera_state = self.CAMERA_STATE_ACTIVE_STOPPED
            self.logger.debug('camera state: %s', self.camera_state)

            # update status of parameters
            self._set_camera_status(ParameterStatus.HARDWARE)
            # update parameter values
            self._update_camera_parameters(cam)
        else:
            self.logger.warning('failed to obtain proxy to camera %s', cam_path)

    def _remove_camera(self, cam_path):
        """Remove camera from active cameras list"""
        self.active_cams = [cam for cam in self.active_cams
                            if cam.object_path != cam_path]

    def _camera_state_changed(self, state):
        self.logger.debug('camera status changed: %d -> %d',
                          self.camera_state, state)

        if state == self.CAMERA_STATE_ACTIVE_RECORDING:
            record_state = 1
        else:
            record_state = 0
        ParametersStore.set('record_state', record_state)

        if (state, self.camera_state) in self.SNAPSHOT_STATES:
            # take snapshot
            self.service.controller.take_snapshot()

        # update current camera state
        self.camera_state = state

    def _camera_parameter_changed(self, key, val):
        self.logger.debug('camera parameter changed: %s: %s', key, val)
        if key not in CAMERA_PARAMETERS:
            self.logger.debug('parameter %s is not a camera parameter', key)
            return
        try:
            ParametersStore.set(key, val)
        except KeyError:
            self.logger.exception('parameter %s = %s not supported', key, val)

    def bus_service_offline(self):
        self.logger.debug('camera controller service gone')
        self.camctl = None
        self._set_camera_status(ParameterStatus.SOFTWARE)
        for cam in self.active_cams:
            del cam
        self.active_cams = []

    def _setup_camctl_proxy(self):
        """Setup proxy to servo service, call only whe name is resolvable"""
        if self.camctl:
            return

        self.logger.debug('obtain proxy to camera controller')
        self.camctl = self.get_proxy(self.DBUS_OBJECT_PATH, self.DBUS_INTERFACE_NAME)

        if self.camctl:
            self.logger.debug('got proxy')
            self.camctl.connect_to_signal('cameraFound', self._camera_found)
            self.camctl.connect_to_signal('cameraDisappeared', self._camera_gone)
            if self._cameras_present():
                self._setup_cameras()
            else:
                self.logger.info('no cameras present in camera controller')
                self._maybe_trigger_discovery()
                self._setup_camera_presence_check()

    def _setup_cameras(self):
        """Setup proxies for all cameras"""
        assert self.camctl

        # list available cameras
        cameras = self.camctl.listCameras()
        if not cameras:
            self.logger.info('no cameras present in camera controller, aborting setup')
        for cam in cameras:
            self.logger.debug('setting up camera %s', cam)
            self._setup_camera(cam)

    def _cameras_present(self):
        """Check if there are any cameras known to camera controller

        :return: True if cameras are present
        """
        if not self.camctl:
            return False

        cameras = self.camctl.listCameras()
        if not cameras:
            self.logger.debug('no cameras present')
            return False
        else:
            return True

    def _maybe_trigger_discovery(self):
        """Trigger camera discovery under condition that no cameras are
        present in camera controller and the last trigger was more
        than DISCOVERY_TIMEOUT seconds away

        :return: True if discovery was triggered

        """
        if self._cameras_present():
            self.logger.debug('cameras present, discovery not needed')
            return False

        if self.last_discovery:
            diff = (datetime.now() - self.last_discovery).total_seconds()
        else:
            diff = self.DISCOVERY_TIMEOUT

        self.logger.debug('last discovery %s seconds ago', diff)
        if diff >= self.DISCOVERY_TIMEOUT:
            self.logger.debug('triggering camera discovery')
            self.last_discovery = datetime.now()
            self.camctl.triggerDiscovery()
            return True
        return False

    def _camera_presence_check(self):
        """Glib timeout callback. Check if camera controller has any
        cameras. If so, perform necessary setup, otherwise, schedule another
        callback"""
        self.logger.debug('camera presence check')
        if not self._cameras_present():
            self._maybe_trigger_discovery()
            self._setup_camera_presence_check()
        return False

    def _setup_camera_presence_check(self):
        """Setup camera presence check to happen in future"""
        self.logger.debug('camera presence check in %s seconds', self.DISCOVERY_TIMEOUT)
        glib.timeout_add_seconds(self.DISCOVERY_TIMEOUT,
                                 self._camera_presence_check)

    def _camera_found(self, cam_path, used):
        """Handler for org.ros3d.CameraController.cameraFound signal"""
        self.logger.debug('found camera %s, used %s', cam_path, used)

        self._setup_camera(cam_path)

    def _camera_gone(self, cam_path):
        """Handler for org.ros3d.CameraController.cameraDisappeared signal"""
        self.logger.debug('camera %s disconnected', cam_path)

        self._remove_camera(cam_path)

    def _is_camera_active(self, cam_path):
        """Check if camera is already active"""
        return bool([cam for cam in self.active_cams
                     if cam_path == cam.object_path])

    def is_active(self):
        """Check if camera controller is active, meaning camera controller is
        present on the bus and active cameras exist"""
        if self.camctl and self.active_cams:
            retval = True
        else:
            retval = False

        self.logger.debug('camctl active? %s', 'yes' if retval else 'no')
        return retval

    @classmethod
    def _get_param(cls, cam, param):
        """Obtain a parameter from camera

        :param cam: camera proxy
        :param param str: parameter name
        :rtype: string
        :return: parameter value
        """
        return cam.getValue(param)

    def _update_camera_parameters(self, cam):
        """Update camera related parameters"""
        self.logger.debug('updating camera parameters')
        for param in CAMERA_PARAMETERS:
            try:
                val = self._get_param(cam, param)
                self.logger.debug('current value: %s -> %s', param, val)
                ParametersStore.set(param, val)
            except dbus.DBusException:
                self.logger.exception('failed to obtain parameter %s from camera %s',
                                      param, cam.object_path)

