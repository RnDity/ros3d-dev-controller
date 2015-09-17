#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#

from ros3ddevcontroller.service import Ros3DKRControllerService, Ros3DAOControllerService
from ros3ddevcontroller.param.store import ParameterLoader


def mainAO():
    # load parameters from file
    ParameterLoader.load()
    # initialize tasks
    Ros3DAOControllerService.initFromCLI()

def mainKR():
    # load parameters from file
    ParameterLoader.load()
    # initialize tasks
    Ros3DKRControllerService.initFromCLI()
