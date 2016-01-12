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
"""Helper wrapper for building DBus client tasks"""

from __future__ import absolute_import
from sparts.tasks.dbus import DBusTask
from sparts.sparts import option
from ros3ddevcontroller.param.store import ParametersStore, CAMERA_PARAMETERS
from ros3ddevcontroller.param.parameter import ParameterStatus, Infinity
import dbus


class DBusClientTask(DBusTask):
    """DBus client task helper class. Inherit this class and override
    bus_service_online() and bus_service_offline() methods. Set
    DBUS_SERVICE_NAME to the name of a DBus service that you want to
    use. The class will automatically setup a name watch and call
    online/offline callbacks when service becomes available.

    """

    OPT_PREFIX = 'dbus-client'

    DBUS_SERVICE_NAME = None

    session_bus = option(action='store_true', type=bool,
                         default=False,
                         help='Use session bus to access service')

    def __init__(self, *args, **kwargs):
        super(DBusClientTask, self).__init__(*args, **kwargs)

        self.bus = None

        assert self.DBUS_SERVICE_NAME != None

    def start(self):
        self.logger.debug('starting client task for DBus service %s',
                          self.DBUS_SERVICE_NAME)
        self.asyncRun(self._setup_bus_client)
        super(DBusClientTask, self).start()

    def _setup_bus_client(self):
        """Start task. Perform necessary setup:
        - bus connection
        - setup service name monitoring
        """
        self.logger.debug('starting dbus client task for service: %s', self.service.name)
        # get bus
        if self.session_bus:
            self.bus = dbus.SessionBus(private=True)
        else:
            self.bus = dbus.SystemBus(private=True)

        self.logger.info('using %s bus for DBus service %s',
                         'session' if self.session_bus else 'system',
                         self.DBUS_SERVICE_NAME)

        # we're monitoring service name changes
        self.bus.watch_name_owner(self.DBUS_SERVICE_NAME,
                                  self._bus_service_name_changed)

    def stop(self):
        """Stop task"""
        # get rid of reference to bus
        self.bus = None

        super(DBusClientTask, self).stop()

    def _bus_service_name_changed(self, name):
        """Callback for when a name owner of bus service has changed

        :param str name: service name, either actual service name or empty
        """

        self.logger.debug('service name changed: %s', name)

        if not name:
            self.logger.info('service lost')
            self.bus_service_offline()
        else:
            self.bus_service_online()

    def bus_service_online(self):
        """Override this method to handle event when the service becomes avaialble"""

    def bus_service_offline(self):
        """Override this method to handle event when the service becomes unavailable"""

    def get_proxy(self, path, interface):
        """Obtain proxy to an interface `interface` defined in
        DBUS_SERVICE_NAME service at path `path`

        :param path str: object path
        :param interface str: interface name
        :return: interface proxy
        """
        assert self.bus
        try:
            obj = self.bus.get_object(self.DBUS_SERVICE_NAME, path)
            iface_proxy = dbus.Interface(obj, interface)
        except dbus.DBusException:
            self.logger.exception('failed to obtain proxy to servo')
            return None
        else:
            return iface_proxy
