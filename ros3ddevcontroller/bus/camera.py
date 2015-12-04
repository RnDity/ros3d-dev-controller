#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""Camera Controller wrapper"""
from __future__ import absolute_import
from ros3ddevcontroller.bus.client import DBusClientTask


class CameraTask(DBusClientTask):
    """Camera Controller proxy
    """
    OPT_PREFIX = 'camera-controller'

    DBUS_SERVICE_NAME = 'org.ros3d.CameraController'
    DBUS_OBJECT_PATH = '/org/ros3d/controller'
    DBUS_INTERFACE_NAME = "org.ros3d.CameraController"
    CAMERA_DBUS_INTERFACE = "org.ros3d.Camera"

    def __init__(self, *args, **kwargs):
        super(CameraTask, self).__init__(*args, **kwargs)

        self.camctl = None

    def start(self):
        super(CameraTask, self).start()

    def bus_service_online(self):
        self.logger.debug('camera controller service available')
        self._setup_camctl_proxy()

    def bus_service_offline(self):
        self.logger.debug('camera controller service gone')
        self.camctl = None

    def _setup_camctl_proxy(self):
        """Setup proxy to servo service, call only whe name is resolvable"""
        if self.camctl:
            return

        self.logger.debug('obtain proxy to camera controller')
        self.camctl = self.get_proxy(self.DBUS_OBJECT_PATH, self.DBUS_INTERFACE_NAME)
        if self.camctl:
            self.logger.debug('got proxy')

    def is_active(self):
        """Check if camera controller can be used"""
        self.logger.debug('camctl active? %s', 'yes' if self.camctl else 'no')
        if self.camctl:
            return True
        return False
