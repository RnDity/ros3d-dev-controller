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


