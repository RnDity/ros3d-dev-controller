#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""System parameters"""

from __future__ import absolute_import

from ros3dkr.param.parameter import Parameter

SYSTEM_PARAMETERS = [
    Parameter('focus_distance_m', 5.0, float),
    Parameter('aperture', 30.0, float),
    Parameter('focal_length_mm', 35, float),
    Parameter('convergence_deg', 0.026, float),
    Parameter('baseline_mm', 80, float)
]
