#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""Broadcasting device controller service using zeroconf"""
from __future__ import absolute_import

from sparts.tasks.dbus import DBusTask
import logging
import dbus
import avahi
from ros3ddevcontroller.util import get_eth_mac

_log = logging.getLogger(__name__)


class ZeroconfTask(DBusTask):
    """Task for handling of registration with Zeroconf service provider"""

    SERVICE_NAME = 'Ros3D dev controller API at {mac}'
    SERVICE_TYPE = "_http._tcp"
    SERVICE_PORT = 0

    def __init__(self, *args, **kwargs):
        super(ZeroconfTask, self).__init__(*args, **kwargs)

        # find MAC address of first ethernet interface
        eth_mac = get_eth_mac()

        self.logger.debug('device MAC address: %s', eth_mac)

        self.service_name = getattr(self.service, 'ZEROCONF_SERVICE_NAME', None)
        if not self.service_name:
            self.service_name = ZeroconfTask.SERVICE_NAME.format(mac=eth_mac)
        self.logger.debug('service name: %s', self.service_name)

        self.server = None
        self.group = None
        self.bus = None

    def start(self):
        assert self.service.options.http_port, \
            'HTTP port not set'
        ZeroconfTask.SERVICE_PORT = self.service.options.http_port
        self.logger.debug('options: %r', self.service.options.http_port)
        self.asyncRun(self._start_avahi)
        super(ZeroconfTask, self).start()

    def _start_avahi(self):
        self.logger.debug('stating avahi in main loop')
        self.bus = dbus.SystemBus(private=True)
        avahi_obj = self.bus.get_object(avahi.DBUS_NAME,
                                        avahi.DBUS_PATH_SERVER)
        self.server = dbus.Interface(avahi_obj,
                                     avahi.DBUS_INTERFACE_SERVER)
        self.server.connect_to_signal('StateChanged',
                                      self._server_state_changed)
        self._server_state_changed(self.server.GetState())

    def _server_state_changed(self, state):
        self.logger.debug("avai state: %d", state)

        if state == avahi.SERVER_RUNNING:
            self.logger.debug('avahi running')
            self._register_dev_controller_service()

    def _register_dev_controller_service(self):
        # get a new group object
        group_path = self.server.EntryGroupNew()
        # bus object
        group_obj = self.bus.get_object(avahi.DBUS_NAME, group_path)
        self.logger.debug('dev controller service object: %s', group_obj)
        # group entry proxy
        group = dbus.Interface(group_obj,
                               avahi.DBUS_INTERFACE_ENTRY_GROUP)
        # watch group registration changes
        group.connect_to_signal('StateChanged',
                                self._group_state_changed)

        description = []
        description.append("system=" + self.service.system_config.get_system())

        self.logger.warning('system description: %s', description)
        group.AddService(avahi.IF_UNSPEC,  # any interface
                         avahi.PROTO_INET, # IPv4
                         dbus.UInt32(0),   # flags
                         self.service_name,
                         ZeroconfTask.SERVICE_TYPE,
                         "", "",
                         dbus.UInt16(ZeroconfTask.SERVICE_PORT),
                         avahi.string_array_to_txt_array(description))
        group.Commit()
        # keep track of group proxy
        self.group = group

    def _group_state_changed(self, state, error):
        self.logger.debug('group state changed: %d, %s', state, error)
        if state == avahi.ENTRY_GROUP_ESTABLISHED:
            self.logger.info('service group registered')
        elif state == avahi.ENTRY_GROUP_COLLISION:
            self.logger.error('service collision detected')
            self.logger.error('failed to register service %s',
                              self.service_name)
