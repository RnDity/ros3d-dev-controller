# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#

from sparts.vservice import VService
from sparts.sparts import option
from ros3dkr.web import WebAPITask
from ros3dkr.bus import Ros3DDBusTask
from ros3dkr.bus.servo import ServoTask
from ros3dkr.bus.zeroconf import ZeroconfTask
from ros3dkr.util import ConfigLoader

class Ros3DKRService(VService):
    """Ros3D KR services wrapper"""

    TASKS = [
        WebAPITask,
        ServoTask,
        ZeroconfTask
    ]

    config_file = option(default=ConfigLoader.DEFAULT_PATH,
                         help='Ros3D configuration file')

    def __init__(self, *args, **kwargs):
        super(Ros3DKRService, self).__init__(*args, **kwargs)

        self.logger.debug('loading configuration from %s',
                          self.options.config_file)
        self.config = ConfigLoader(self.options.config_file)
