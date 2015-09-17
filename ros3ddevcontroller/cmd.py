#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#

from ros3ddevcontroller.service import Ros3DdevControllerService
from ros3ddevcontroller.param.store import ParameterLoader


def main():
    # load parameters from file
    ParameterLoader.load()
    # initialize tasks
    Ros3DdevControllerService.initFromCLI()

