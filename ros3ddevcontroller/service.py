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
from sparts.vservice import VService
from sparts.sparts import option
from sparts.compat import captureWarnings
from ros3ddevcontroller.web import WebAPITask
from ros3ddevcontroller.bus import Ros3DDBusTask
from ros3ddevcontroller.bus.servo import ServoTask
from ros3ddevcontroller.bus.zeroconf import ZeroconfTask
from ros3ddevcontroller.bus.camera import CameraTask
from ros3ddevcontroller.util import SystemConfigLoader, ControllerConfigLoader, get_eth_mac
from ros3ddevcontroller.mqtt import MQTTTask
from ros3ddevcontroller.controller import Controller
import logging
import sys


class Ros3DdevControllerService(VService):
    """Ros3D device controller services wrapper"""

    system_config_file = option(default=SystemConfigLoader.DEFAULT_PATH,
                                help='Ros3D system configuration file')
    config_file = option(default=ControllerConfigLoader.DEFAULT_PATH,
                         help='Ros3D controller configuration file')

    def __init__(self, *args, **kwargs):
        super(Ros3DdevControllerService, self).__init__(*args, **kwargs)

        self.logger.debug('loading controller configuration from %s',
                          self.options.config_file)
        self.config = ControllerConfigLoader(self.options.config_file)
        self.logger.debug('loading system configuration from %s',
                          self.options.system_config_file)
        self.system_config = SystemConfigLoader(self.options.system_config_file)

        self.controller = Controller()
        self.controller.set_snapshots_location(self.config.get_snapshots_location())

    def initLogging(self):
        """Setup logging to stderr"""
        logging.basicConfig(level=self.loglevel, stream=sys.stderr,
                            format='%(thread)d %(asctime)s - %(name)s - %(levelname)s - %(message)s')

        captureWarnings(True)


class Ros3DAOControllerService(Ros3DdevControllerService):
    """Ros3D ao device controller services wrapper"""

    ZEROCONF_SERVICE_NAME = 'Ros3D AO dev controller API at {mac}'.format(mac=get_eth_mac())
    TASKS = [
        WebAPITask,
        ZeroconfTask,
        MQTTTask
    ]


class Ros3DKRControllerService(Ros3DdevControllerService):
    """Ros3D kr device controller services wrapper"""

    ZEROCONF_SERVICE_NAME = 'Ros3D KR dev controller API at {mac}'.format(mac=get_eth_mac())
    TASKS = [
        WebAPITask,
        ServoTask,
        ZeroconfTask,
        MQTTTask,
        CameraTask,
    ]

    def initService(self):
        self.controller.set_servo(self.getTask(ServoTask))
        self.controller.set_camera(self.getTask(CameraTask))
