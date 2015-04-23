#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""Implementation of Ros3D KR MQTT API"""

from __future__ import absolute_import
from sparts.tasks.tornado import TornadoTask

import logging
from ros3dkr.param  import ParametersStore

_log = logging.getLogger(__name__)

class MQTTTask(TornadoTask):

    def start(self):
        _log.debug('task started')
