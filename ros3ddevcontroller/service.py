# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#

from sparts.vservice import VService
from sparts.sparts import option
from sparts.compat import captureWarnings
from ros3ddevcontroller.web import WebAPITask
from ros3ddevcontroller.bus import Ros3DDBusTask
from ros3ddevcontroller.bus.servo import ServoTask
from ros3ddevcontroller.bus.zeroconf import ZeroconfTask
from ros3ddevcontroller.util import ConfigLoader
from ros3ddevcontroller.mqtt import MQTTTask
import logging
import sys


class Ros3DdevControllerService(VService):
    """Ros3D device controller services wrapper"""

    config_file = option(default=ConfigLoader.DEFAULT_PATH,
                         help='Ros3D configuration file')

    def __init__(self, *args, **kwargs):
        super(Ros3DdevControllerService, self).__init__(*args, **kwargs)

        self.logger.debug('loading configuration from %s',
                          self.options.config_file)
        self.config = ConfigLoader(self.options.config_file)

    def initLogging(self):
        """Setup logging to stderr"""
        logging.basicConfig(level=self.loglevel, stream=sys.stderr,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        captureWarnings(True)

class Ros3DAOControllerService(Ros3DdevControllerService):
    """Ros3D ao device controller services wrapper"""

    TASKS = [
        WebAPITask,
        ZeroconfTask,
        MQTTTask
    ]


class Ros3DKRControllerService(Ros3DdevControllerService):
    """Ros3D kr device controller services wrapper"""

    TASKS = [
        WebAPITask,
        ServoTask,
        ZeroconfTask,
        MQTTTask
    ]
