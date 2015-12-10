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

    def test_baseline_changed(self):

        #Set initial values
        ParametersStore.set('frame_width_px', 1920, evaluate=False)
        ParametersStore.set('focal_length_mm', 25, evaluate=False)
        ParametersStore.set('baseline_mm', 50.0, evaluate=False)
        ParametersStore.set('frame_width_mm', 15.84, evaluate=False)
        ParametersStore.set('distance_screen_m', 5.2, evaluate=False)
        ParametersStore.set('distance_object1_m', 4.4, evaluate=False)
        ParametersStore.set('distance_object2_m', 9.5, evaluate=False)

        #Change baseline to different value so convergence evaluation starts
        ParametersStore.set('baseline_mm', 20, evaluate=True)

        #Check new values
        convergence_px = ParametersStore.get_value('convergence_px')
        self.assertEquals(round(convergence_px, 2), 12.03)

        convergence_deg = ParametersStore.get_value('convergence_deg')
        self.assertEquals(round(convergence_deg, 2), 0.22)
