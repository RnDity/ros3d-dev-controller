#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""Implementation of Ros3D KR MQTT API"""

from __future__ import absolute_import
from sparts.tasks.tornado import TornadoTask
from sparts.sparts import option

from ros3dkr.param  import ParametersStore

import paho.mqtt.client as mqtt
import logging

from ros3dkr.mqtt.mqttornado import MQTTornadoAdapter

_log = logging.getLogger(__name__)

class MQTTTask(TornadoTask):

    OPT_PREFIX = 'mqtt'
    port = option(default = 1883, help = 'Broker port')
    host = option(default = 'localhost', help = 'Broker host address')

    def __init__(self, *args, **kwargs):
        super(MQTTTask, self).__init__(*args, **kwargs)

        self.adapter = None

        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

    def start(self):
        self.logger.debug('start')
        self._try_connect()       

    def stop(self):
        self.logger.debug('stop')

    def _try_connect(self):
        """Attempt connection, if not schedule a reconnect after  timeout  """
        self.logger.debug('trying to connect to %s:%d', self.host, self.port)
        try:
            self._connect()
        except socket.error:
            self.logger.debug('failed to connect')
            self._schedule_reconnect()

    def _connect(self):
        self.logger.debug('connect')
        self.client.connect(self.host, self.port)
        self.adapter = MQTTornadoAdapter(self.client)

    def _schedule_reconnect(self):
        """Schedule reconnection attempt"""
        # reconnect after 10s
        timeout = 10

        self.logger.debug('reconnect after %d seconds', timeout)
       
        loop = self.ioloop
        loop.add_timeout(loop.time() + timeout, self._try_connect)

    def _on_connect(self, client, userdata, flags, rc):
        """CONNACK received"""
        self.log.debug('connected: %s', mqtt.connack_string(rc))
        self.log.debug('flags: %s', flags)

        self.adapter.poll_writes()

    def _on_disconnect(self, client, userdata, rc):
         """DISCONNECT received"""
         self.log.debug('disconnected: %s', mqtt.connack_string(rc))

         self.adapter.stop()
         self.adapter = None
         self._schedule_reconnect()
