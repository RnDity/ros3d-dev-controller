#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""System parameters wrappers"""

from __future__ import absolute_import

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


class DofNearCalc(Evaluator):
    pass


class DofFarCalc(Evaluator):
    pass


class DofTotalCalc(Evaluator):
    pass


class FovHorizontalDegCalc(Evaluator):
    pass


class FovVerticalDegCalc(Evaluator):
    pass


class FovDiagonalDegCalc(Evaluator):
    pass


class ConvergenceDegCalc(Evaluator):
    pass


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


