#
# Copyright (c) 2015 Open-RnD Sp. z o.o.
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use, copy,
# modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
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

    def test_focal_length_changed(self):

        #Set initial values
        ParametersStore.set('focal_length_mm', 25, evaluate=False)
        ParametersStore.set('baseline_mm', 50.0, evaluate=False)
        ParametersStore.set('frame_width_mm', 15.84, evaluate=False)
        ParametersStore.set('frame_height_mm', 8.91, evaluate=False )
        ParametersStore.set('distance_screen_m', 3.15, evaluate=False)
        ParametersStore.set('distance_near_m', 1.04, evaluate=False)

        #Change focal_length to check evaluation
        ParametersStore.set('focal_length_mm', 20, evaluate=True)

        #Check new values
        parallax_near_percent = ParametersStore.get_value('parallax_near_percent')
        self.assertEquals(round(parallax_near_percent, 2), -4.07)

        real_width_near_m = ParametersStore.get_value('real_width_near_m')
        self.assertEquals(round(real_width_near_m, 2), 0.82)

        real_height_near_m = ParametersStore.get_value('real_height_near_m')
        self.assertEquals(round(real_height_near_m, 2), 0.46)
