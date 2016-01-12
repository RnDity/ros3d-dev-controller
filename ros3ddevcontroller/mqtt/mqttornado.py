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
"""MQTT to Tornado adapter"""

import logging
from tornado.ioloop import IOLoop, PeriodicCallback

# periodic check with MQTT client library to execute misc actions
# (pings, etc.)
MQTT_MISC_PERIOD = 10 * 1000

LOG = logging.getLogger('mqttornado')

class MQTTornadoAdapter(object):
    """Adapter for interfacing MQTT Client with Tornado framework"""

    def __init__(self, client, loop=None):
        """Create new adapter for given client instance

        :param mqtt.Client client: MQTT client instance
        :param tornado.ioloop.IOLoop loop: Tonardo IOLoop instance,
                                           None to use default loop
        """
        self._client = client
        self._fd = self._client_fd()
        self._loop = loop
        self._read_events = IOLoop.READ | IOLoop.ERROR
        self._all_events = self._read_events | IOLoop.WRITE

        if not self._loop:
            self._loop = IOLoop.instance()

        LOG.debug('setup handlers')
        self._loop.add_handler(self._client_fd(),
                               self._io_clbk,
                               self._all_events)

        self._periodic = PeriodicCallback(self._periodic_clbk,
                                          MQTT_MISC_PERIOD,
                                          io_loop=self._loop)
        self._periodic.start()

    def stop(self):
        """Stop Adapter

        """
        self._loop.remove_handler(self._fd)
        self._periodic.stop();
        self._periodic = None

    def _client_fd(self):
        """Return MQTT client FD if already set otherwise raise an
        exception

        :rtype: int
        :return: MQTT client fd
        """
        sock = self._client.socket()

        if sock == None:
            raise RuntimeError('not connected to broker')
        LOG.debug('socket: %s', sock.fileno())
        return sock.fileno()

    def _io_clbk(self, _, event):
        """IO Callback from Tornado"""

        LOG.debug('IO event: 0x%x', event)

        if event & IOLoop.READ:
            self._client.loop_read()

        if event & IOLoop.ERROR:
            self._client.loop_read()

        if event & IOLoop.WRITE:
            self._client.loop_write()

        if self.poll_writes() == False:
            self._loop.update_handler(self._client_fd(),
                                      self._read_events)

    def _periodic_clbk(self):
        """Periodic callback handler"""
        # LOG.debug('periodic check')
        self._client.loop_misc()

    def poll_writes(self):
        """Check if client wants to write anything and schedule write
        action

        :return: True if client wants to write, False otherwise
        :rtype: bool"""
        if self._client.want_write():
            LOG.debug('want write')
            self._loop.update_handler(self._client_fd(),
                                      self._all_events)
            return True
        return False
