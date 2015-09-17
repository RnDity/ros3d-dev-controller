#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""Implementation of Ros3D device controller MQTT API"""

from __future__ import absolute_import
from sparts.tasks.tornado import TornadoTask
from sparts.sparts import option

from ros3ddevcontroller.mqtt.mqttornado import MQTTornadoAdapter
from ros3ddevcontroller.web.codec import ParameterCodec
from ros3ddevcontroller.param  import ParametersStore

import paho.mqtt.client as mqtt
import logging
import socket

_log = logging.getLogger(__name__)

class MQTTTask(TornadoTask):

    OPT_PREFIX = 'mqtt'
    port = option(default=1883, help='Broker port')
    host = option(default='localhost', help='Broker host address')
    topic = option(default='/parameters', help='Parameters topic')

    def __init__(self, *args, **kwargs):
        super(MQTTTask, self).__init__(*args, **kwargs)

        self.adapter = None

        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

    def start(self):
        _log.debug('start')
        self.ioloop.add_callback(self._try_connect)
        ParametersStore.change_listeners.add(self.param_changed)

    def stop(self):
        _log.debug('stop')
        if self.adapter is not None:
            self.adapter.stop()
        #self.client.disconnect()
        ParametersStore.change_listeners.remove(self.param_changed)

    def _try_connect(self):
        """Attempt connection, if not schedule a reconnect after  timeout  """
        _log.debug('try connecting to broker')
        try:
            self._connect()
        except socket.error:
            _log.warning('failed to connect')
            self._schedule_reconnect()

    def _connect(self):
        _log.debug('connect to %s:%d', self.host, int(self.port))
        self.client.connect(self.host, self.port)
        self.adapter = MQTTornadoAdapter(self.client)

    def _schedule_reconnect(self):
        """Schedule reconnection attempt"""
        # reconnect after 10s
        timeout = 10

        _log.debug('reconnect after %d seconds', timeout)

        loop = self.ioloop
        _log.debug('reconnect at %d (now %d)',
                   loop.time() + timeout, loop.time())
        loop.add_timeout(loop.time() + timeout, self._try_connect)

    def _on_connect(self, client, userdata, flags, rc):
        """CONNACK received"""
        _log.debug('connected: %s', mqtt.connack_string(rc))
        _log.debug('flags: %s', flags)
        self.adapter.poll_writes()

    def _on_disconnect(self, client, userdata, rc):
        """DISCONNECT received"""
        _log.debug('disconnected: %s', mqtt.connack_string(rc))

        self.adapter.stop()
        self.adapter = None
        self._schedule_reconnect()

    def param_changed(self, param):
        _log.debug('param_changed %s', param)
        self.ioloop.add_callback(self._publish_param, param)

    def _publish_param(self, param):
        as_json = ParameterCodec(as_set=True).encode(param)
        _log.debug('publish to %s: %s', self.topic, as_json)
        self.client.publish(self.topic, as_json)
