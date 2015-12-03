#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""System parameters wrappers"""

from __future__ import absolute_import

import math
import logging

_log = logging.getLogger(__name__)


class ParameterStatus(object):
    """Paramter status wrapper"""
    HARDWARE = 'hardware'
    SOFTWARE = 'software'

    def __init__(self, read=True, write=True,
                 status_type=SOFTWARE):
        self.read = read
        self.write = write
        self.status = status_type

    def set_status(self, status):
        """Set parameter status

        :param status: one of HARDWARE, SOFTWARE"""
        if status not in [ParameterStatus.HARDWARE, ParameterStatus.SOFTWARE]:
            raise ValueError('invalid status {}'.format(status))
        self.status = status


class Parameter(object):
    """System parameter wrapper"""

    def __init__(self, name, value, value_type,
                 status=None, min_val=None, max_val=None,
                 evaluated=False, evaluator=None):
        """Initialize a parameter

        :param str name: parameter name
        :param value: parameter value, corresponding to value_type
        :param typr value_type: type of parameter value
        :param ParameterStatus status: status info, if None, defaults to a hardware paramter
        :param min_val: minimum value
        :param max_val: maximum value
        :param evaluated: True if value is evaluated
        :param evaluator: Class that will be called to evaluate the parameter
        """
        self.name = name
        self.value = value
        self.value_type = value_type

        if not status:
            self.status = ParameterStatus(read=True, write=True,
                                          status_type=ParameterStatus.SOFTWARE)
        else:
            assert isinstance(status, ParameterStatus)
            self.status = status

        self.min_value = min_val
        self.max_value = max_val

        self.evaluated = evaluated
        self.evaluator = evaluator

    def is_read_only(self):
        return self.status.write == False


class ReadOnlyParameter(Parameter):
    """Read only parameter wrapper"""

    def __init__(self, name, value, value_type, **kwargs):
        super(ReadOnlyParameter, self).__init__(name, value, value_type,
                                                status=ParameterStatus(write=False),
                                                **kwargs)


class Evaluator(object):
    NAME = 'unset'

    def __call__(self):
        raise NotImplementedError('Evaluation for {} not implemented'.format(self.__name__))

class DofHelperCalc(Evaluator):

    REQUIRES = [
        'focus_distance_m',
        'focal_length_mm',
        'aperture',
        'coc_um'
        'frame_width_px',
        'sensor_width_px'
    ]

    @staticmethod
    def calc_h_hs():
        focal_length = ParametersStore.get('focal_length_mm').value
        aperture = ParametersStore.get('aperture').value
        frame_width_px = ParametersStore.get('frame_width_px').value
        sensor_width_px = ParametersStore.get('sensor_width_px').value
        coc_um = ParametersStore.get('coc_um').value

        coc_mm = coc_um / 1000.
        ratio = frame_width_px / sensor_width_px
        h = 0.001 * (focal_length * focal_length) / (coc_mm * ratio * aperture)
        hs = h * focus

        return h, hs

class DofNearCalc(DofHelperCalc):

    def __call__(self):
        coc_um = ParametersStore.get('coc_um').value
        focus = ParametersStore.get('focus_distance_m').value

        if coc_um == 0:
            return focus

        h, hs = DofHelperCalc.calc_h_hs()

        if focus == float('inf'):
            return h

        near = hs / (h + focus)
        return near

class DofFarCalc(DofHelperCalc):

    def __call__(self):
        coc_um = ParametersStore.get('coc_um').value
        focus = ParametersStore.get('focus_distance_m').value

        if coc_um == 0:
            return focus

        if focus == float('inf'):
            return float('inf')

        h, hs = DofHelperCalc.calc_h_hs()
        far = inf if focus >= h else (hs / (h - focus))
        return far

class DofTotalCalc(Evaluator):

    REQUIRES = [
        'dof_near_m',
        'dof_far_m'
    ]

    def __call__(self):
        dof_far = ParametersStore.get('dof_near_m').value
        dof_near = ParametersStore.get('dof_near_m').value
        return dof_far.value - dof_near.value

class FovHorizontalDegCalc(Evaluator):
    pass


class FovVerticalDegCalc(Evaluator):
    pass


class FovDiagonalDegCalc(Evaluator):
    pass


class ConvergenceDegCalc(Evaluator):

    REQUIRES = [
        'baseline_mm',
        'distance_screen_m'
    ]

    def __call__(self):
        baseline = ParametersStore.get('baseline_mm').value
        screen = ParametersStore.get('distance_screen_m').value
        return 2 * math.degrees(math.atan((baseline / 2) / screen))

class ConvergencePxCalc(Evaluator):
    pass


class ParallaxNearPercentCalc(Evaluator):
    pass


class ParallaxScreenPercentCalc(Evaluator):
    pass


class ParallaxFarPercentCalc(Evaluator):
    pass


class ParallaxObject1PercentCalc(Evaluator):
    pass


class ParallaxObject2PercentCalc(Evaluator):
    pass


class ParallaxNearMMCalc(Evaluator):
    pass


class ParallaxScreenMMCalc(Evaluator):
    pass


class ParallaxFarMMCalc(Evaluator):
    pass


class ParallaxObject1MMCalc(Evaluator):
    pass


class ParallaxObject2MMCalc(Evaluator):
    pass


class RealWidthNearCalc(Evaluator):
    pass


class RealHeightNearCalc(Evaluator):
    pass


class RealWidthScreenCalc(Evaluator):
    pass


class RealHeightScreenCalc(Evaluator):
    pass


class RealHeightFarCalc(Evaluator):
    pass


class RealHeightFarCalc(Evaluator):
    pass


class RealHeightObject1Calc(Evaluator):
    pass


class RealWidthObject1Calc(Evaluator):
    pass


class RealWidthObject2Calc(Evaluator):
    pass


class RealHeightObject2Calc(Evaluator):
    pass


class FrameWidthMMCalc(Evaluator):
    pass


class FrameDiagonalMMCalc(Evaluator):
    pass


class FrameHorizontalCropCalc(Evaluator):
    pass


class FrameVerticalCropCalc(Evaluator):
    pass


class FrameDiagonalCropCalc(Evaluator):
    pass


class CocUmCalc(Evaluator):
    pass


class ScreenDistanceCalc(Evaluator):
    pass


class SpectatorFovHorizontalDegCalc(Evaluator):
    pass


class PerceivedPositionNearPercCalc(Evaluator):
    pass


class PerceivedPositionScreenPercCalc(Evaluator):
    pass


class PerceivedPositionFarPercCalc(Evaluator):
    pass


class PerceivedPositionObject1PercCalc(Evaluator):
    pass


class PerceivedPositionObject2PercCalc(Evaluator):
    pass


class PerceivedPositionNearMCalc(Evaluator):
    pass


class PerceivedPositionScreenMCalc(Evaluator):
    pass


class PerceivedPositionFarMCalc(Evaluator):
    pass


class PerceivedPositionObject1MCalc(Evaluator):
    pass


class PerceivedPositionObject2MCalc(Evaluator):
    pass


