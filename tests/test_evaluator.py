#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""Evaluator tests"""
from __future__ import absolute_import, print_function
import unittest

from ros3ddevcontroller.param.store import ParametersStore, ParameterLoader
from ros3ddevcontroller.param.parameter import Parameter, Evaluator
from ros3ddevcontroller.param.sysparams import SYSTEM_PARAMETERS

class EvaluationTestCase(unittest.TestCase):

    def setUp(self):
        #Load system parameters
        ParametersStore.clear_parameters()
        ParametersStore.load_parameters(SYSTEM_PARAMETERS)

    def tearDown(self):
        ParametersStore.clear_parameters()
