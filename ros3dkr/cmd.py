#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#

from ros3dkr.service import Ros3DKRService
from ros3dkr.param.store import ParameterLoader

def main():
    # load parameters from file
    ParameterLoader.load()
    # initialize tasks
    Ros3DKRService.initFromCLI()

