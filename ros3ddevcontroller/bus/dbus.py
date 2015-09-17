#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""DBus components of Ros3D device controller"""

from __future__ import absolute_import

import logging
from sparts.tasks.dbus import DBusServiceTask
import dbus
import dbus.service

_log = logging.getLogger(__name__)


class Ros3DdevControllerBusObject(dbus.service.Object):
    """Implementation of Ros3D device controller DBus service"""

    def __init__(self, dbus_service):
        _log.debug('init DBus service in task: %s', dbus_service.name)
        self._bus = dbus_service.bus
        path = '/org/ros3d/devcontroller'
        dbus.service.Object.__init__(self, self._bus, '/org/ros3d/devcontroller')


class Ros3DDBusTask(DBusServiceTask):
    """DBus service wrapper for device controller"""

    BUS_NAME = 'org.ros3d.devcontroller'
    BUS_CLASS = Ros3DdevControllerBusObject


