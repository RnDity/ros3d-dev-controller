# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#

from sparts.vservice import VService
from sparts.sparts import option
from sparts.compat import captureWarnings
from ros3dkr.web import WebAPITask
from ros3dkr.bus import Ros3DDBusTask
from ros3dkr.bus.servo import ServoTask
from ros3dkr.bus.zeroconf import ZeroconfTask
from ros3dkr.util import ConfigLoader
from ros3dkr.mqtt import MQTTTask
import logging
import sys


class Ros3DKRService(VService):
    """Ros3D KR services wrapper"""

    TASKS = [
        WebAPITask,
        ServoTask,
        ZeroconfTask,
        MQTTTask
    ]

    config_file = option(default=ConfigLoader.DEFAULT_PATH,
                         help='Ros3D configuration file')

    def __init__(self, *args, **kwargs):
        super(Ros3DKRService, self).__init__(*args, **kwargs)

        self.logger.debug('loading configuration from %s',
                          self.options.config_file)
        self.config = ConfigLoader(self.options.config_file)

    def initLogging(self):
        """Setup logging to stderr"""
        logging.basicConfig(level=self.loglevel, stream=sys.stderr,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        captureWarnings(True)
