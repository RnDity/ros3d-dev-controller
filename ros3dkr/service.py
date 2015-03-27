# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#

from sparts.vservice import VService
from ros3dkr.web import WebAPITask
from ros3dkr.bus import Ros3DDBusTask
from ros3dkr.bus.servo import ServoTask

class Ros3DKRService(VService):
    """Ros3D KR services wrapper"""

    TASKS = [
        WebAPITask,
        Ros3DDBusTask,
        ServoTask
    ]
