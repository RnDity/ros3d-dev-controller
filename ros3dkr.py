#!/usr/bin/env python2
#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#

import logging
import argparse
from ros3dkr.service import Ros3DKRService


def main():
    Ros3DKRService.initFromCLI()


if __name__ == '__main__':
    main()
