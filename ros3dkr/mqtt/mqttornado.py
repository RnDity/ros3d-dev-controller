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
