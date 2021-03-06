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
"""Parameter evaluators"""

from ros3ddevcontroller.param.parameter import Evaluator
import math

class DiagonalHelperCalc(Evaluator):

    REQUIRES = []

    @staticmethod
    def calc_diag(width=None, height=None):
        return math.sqrt(width * width + height * height);

class DofHelperCalc(Evaluator):

    REQUIRES = [
        'focus_distance_m',
        'focal_length_mm',
        'aperture',
        'coc_um',
        'frame_width_px',
        'sensor_width_px'
    ]

    @staticmethod
    def calc_h_hs(coc_um=None, focus_distance_m=None, aperture=None,
                  frame_width_px=None, sensor_width_px=None, focal_length_mm=None):

        coc_mm = coc_um / 1000.
        ratio = frame_width_px / sensor_width_px
        h = 0.001 * (focal_length_mm * focal_length_mm) / (coc_mm * ratio * aperture)
        hs = h * focus_distance_m

        return h, hs


class DofNearCalc(DofHelperCalc):

    def __call__(self, coc_um=None, focus_distance_m=None, aperture=None,
                 frame_width_px=None, sensor_width_px=None, focal_length_mm=None):

        if coc_um == 0:
            return focus_distance_m

        h, hs = DofHelperCalc.calc_h_hs(coc_um, focus_distance_m, aperture,
                                        frame_width_px, sensor_width_px, focal_length_mm)

        if focus_distance_m == float('inf'):
            return h

        near = hs / (h + focus_distance_m)
        return near


class DofFarCalc(DofHelperCalc):

    def __call__(self, coc_um=None, focus_distance_m=None, aperture=None,
                 frame_width_px=None, sensor_width_px=None, focal_length_mm=None):

        if coc_um == 0:
            return focus_distance_m

        if focus_distance_m == float('inf'):
            return float('inf')

        h, hs = DofHelperCalc.calc_h_hs(coc_um, focus_distance_m, aperture,
                                        frame_width_px, sensor_width_px, focal_length_mm)
        far = float('inf') if focus_distance_m >= h else (hs / (h - focus_distance_m))
        return far


class DofTotalCalc(Evaluator):

    REQUIRES = [
        'dof_near_m',
        'dof_far_m'
    ]

    def __call__(self, dof_near_m=None, dof_far_m=None):
        return dof_far_m - dof_near_m

class FovDegHelperCalc(Evaluator):

    REQUIRES = [
        'focal_length_mm'
    ]

    @staticmethod
    def calc_fov(focal_length_mm=None, size=None):
        return 2 * math.degrees(math.atan(size / (2 * focal_length_mm)));

class FovHorizontalDegCalc(FovDegHelperCalc):

    REQUIRES = FovDegHelperCalc.REQUIRES + ['frame_width_mm']

    def __call__(self, focal_length_mm=None, frame_width_mm=None):
        return FovDegHelperCalc.calc_fov(focal_length_mm,
                                         frame_width_mm)

class FovVerticalDegCalc(FovDegHelperCalc):

    REQUIRES = FovDegHelperCalc.REQUIRES + ['frame_height_mm']

    def __call__(self, focal_length_mm=None, frame_height_mm=None):
        return FovDegHelperCalc.calc_fov(focal_length_mm,
                                         frame_height_mm)

class FovDiagonalDegCalc(FovDegHelperCalc):

    REQUIRES = FovDegHelperCalc.REQUIRES + [
        'frame_height_mm',
        'frame_width_mm'
    ]

    def __call__(self, focal_length_mm=None,
                 frame_width_mm=None, frame_height_mm=None):

        diag = DiagonalHelperCalc.calc_diag(frame_width_mm, frame_height_mm)
        return FovDegHelperCalc.calc_fov(focal_length_mm, diag)

class ConvergenceDegCalc(Evaluator):

    REQUIRES = [
        'baseline_mm',
        'distance_screen_m'
    ]

    def __call__(self, baseline_mm=None, distance_screen_m=None):
        return 2 * math.degrees(math.atan((baseline_mm / 2) / (1000 * distance_screen_m)))


class ConvergencePxCalc(Evaluator):

    REQUIRES = [
        'frame_width_px',
        'baseline_mm',
        'distance_screen_m',
        'frame_width_mm',
        'focal_length_mm'
    ]

    def __call__(self, frame_width_px=None, baseline_mm=None, distance_screen_m=None,
                 frame_width_mm=None, focal_length_mm=None):
        return frame_width_px * math.atan(baseline_mm / (2 * 1000 * distance_screen_m))  / math.atan(frame_width_mm / (2 * focal_length_mm))


class ParallaxPercentHelperCalc(Evaluator):

    REQUIRES = [
        'baseline_mm',
        'focal_length_mm',
        'frame_width_mm',
        'distance_screen_m'
    ]

    @staticmethod
    def calc_parallax_percent(baseline_mm, focal_length_mm, frame_width_mm,
                              distance_screen_m, distance):

        return 100 * (baseline_mm * focal_length_mm) / frame_width_mm * (1 / (1000 * distance_screen_m) - 1 / (1000 * distance))


class ParallaxNearPercentCalc(ParallaxPercentHelperCalc):

    REQUIRES = ParallaxPercentHelperCalc.REQUIRES + ['distance_near_m']

    def __call__(self, baseline_mm=None, focal_length_mm=None, frame_width_mm=None,
                 distance_screen_m=None, distance_near_m=None):

        return ParallaxPercentHelperCalc.calc_parallax_percent(baseline_mm,
                                                               focal_length_mm,
                                                               frame_width_mm,
                                                               distance_screen_m,
                                                               distance_near_m)


class ParallaxFarPercentCalc(ParallaxPercentHelperCalc):

    REQUIRES = ParallaxPercentHelperCalc.REQUIRES + ['distance_far_m']

    def __call__(self, baseline_mm=None, focal_length_mm=None, frame_width_mm=None,
                 distance_screen_m=None, distance_far_m=None):
        return ParallaxPercentHelperCalc.calc_parallax_percent(baseline_mm,
                                                               focal_length_mm,
                                                               frame_width_mm,
                                                               distance_screen_m,
                                                               distance_far_m)

class ParallaxObject1PercentCalc(ParallaxPercentHelperCalc):

    REQUIRES = ParallaxPercentHelperCalc.REQUIRES + ['distance_object1_m']

    def __call__(self, baseline_mm=None, focal_length_mm=None, frame_width_mm=None,
                 distance_screen_m=None, distance_object1_m=None):

        return ParallaxPercentHelperCalc.calc_parallax_percent(baseline_mm,
                                                               focal_length_mm,
                                                               frame_width_mm,
                                                               distance_screen_m,
                                                               distance_object1_m)

class ParallaxObject2PercentCalc(ParallaxPercentHelperCalc):

    REQUIRES = ParallaxPercentHelperCalc.REQUIRES + ['distance_object2_m']

    def __call__(self, baseline_mm=None, focal_length_mm=None, frame_width_mm=None,
                 distance_screen_m=None, distance_object2_m=None):

        return ParallaxPercentHelperCalc.calc_parallax_percent(baseline_mm,
                                                               focal_length_mm,
                                                               frame_width_mm,
                                                               distance_screen_m,
                                                               distance_object2_m)

class ParallaxMmHelperCalc(Evaluator):

    REQUIRES = [
        'screen_width_m'
    ]

    @staticmethod
    def calc_parallax_mm(screen_width_m=None, parallax_percent=None):

        return 10 * screen_width_m * parallax_percent;

class ParallaxNearMMCalc(ParallaxMmHelperCalc):

    REQUIRES = ParallaxMmHelperCalc.REQUIRES + ['parallax_near_percent']

    def __call__(self, screen_width_m=None, parallax_near_percent=None):

        return ParallaxMmHelperCalc.calc_parallax_mm(screen_width_m,
                                                     parallax_near_percent)

class ParallaxFarMMCalc(ParallaxMmHelperCalc):

    REQUIRES = ParallaxMmHelperCalc.REQUIRES + ['parallax_far_percent']

    def __call__(self, screen_width_m=None, parallax_far_percent=None):

        return ParallaxMmHelperCalc.calc_parallax_mm(screen_width_m,
                                                     parallax_far_percent)

class ParallaxObject1MMCalc(ParallaxMmHelperCalc):

    REQUIRES = ParallaxMmHelperCalc.REQUIRES + ['parallax_object1_percent']

    def __call__(self, screen_width_m=None, parallax_object1_percent=None):
        return ParallaxMmHelperCalc.calc_parallax_mm(screen_width_m,
                                                     parallax_object1_percent)

class ParallaxObject2MMCalc(ParallaxMmHelperCalc):

    REQUIRES = ParallaxMmHelperCalc.REQUIRES + ['parallax_object2_percent']

    def __call__(self, screen_width_m=None, parallax_object2_percent=None):
        return ParallaxMmHelperCalc.calc_parallax_mm(screen_width_m,
                                                     parallax_object2_percent)

class RealHeightHelperCalc(Evaluator):

    REQUIRES = [
        'fov_vertical_deg'
    ]

    @staticmethod
    def calc_real_height(fov_vertical_deg=None, distance=None):
        return 2 * distance * math.tan(math.radians(fov_vertical_deg / 2));

class RealWidthHelperCalc(Evaluator):

    REQUIRES = [
        'fov_horizontal_deg'
    ]

    @staticmethod
    def calc_real_width(fov_horizontal_deg=None, distance=None):
        return 2 * distance * math.tan(math.radians(fov_horizontal_deg / 2));

class RealWidthNearCalc(RealWidthHelperCalc):

    REQUIRES = RealWidthHelperCalc.REQUIRES + ['distance_near_m']

    def __call__(self, fov_horizontal_deg=None, distance_near_m=None):
        return RealWidthHelperCalc.calc_real_width(fov_horizontal_deg,
                                                  distance_near_m)

class RealHeightNearCalc(RealHeightHelperCalc):

    REQUIRES = RealHeightHelperCalc.REQUIRES + ['distance_near_m']

    def __call__(self, fov_vertical_deg=None, distance_near_m=None):
        return RealHeightHelperCalc.calc_real_height(fov_vertical_deg,
                                                     distance_near_m)

class RealWidthScreenCalc(RealWidthHelperCalc):

    REQUIRES = RealWidthHelperCalc.REQUIRES + ['distance_screen_m']

    def __call__(self, fov_horizontal_deg=None, distance_screen_m=None):
        return RealWidthHelperCalc.calc_real_width(fov_horizontal_deg,
                                                  distance_screen_m)

class RealHeightScreenCalc(RealHeightHelperCalc):

    REQUIRES = RealHeightHelperCalc.REQUIRES + ['distance_screen_m']

    def __call__(self, fov_vertical_deg=None, distance_screen_m=None):
        return RealHeightHelperCalc.calc_real_height(fov_vertical_deg,
                                                     distance_screen_m)

class RealWidthFarCalc(RealWidthHelperCalc):

    REQUIRES = RealWidthHelperCalc.REQUIRES + ['distance_far_m']

    def __call__(self, fov_horizontal_deg=None, distance_far_m=None):
        return RealWidthHelperCalc.calc_real_width(fov_horizontal_deg,
                                                  distance_far_m)

class RealHeightFarCalc(RealHeightHelperCalc):

    REQUIRES = RealHeightHelperCalc.REQUIRES + ['distance_far_m']

    def __call__(self, fov_vertical_deg=None, distance_far_m=None):
        return RealHeightHelperCalc.calc_real_height(fov_vertical_deg,
                                                     distance_far_m)

class RealWidthObject1Calc(RealWidthHelperCalc):

    REQUIRES = RealWidthHelperCalc.REQUIRES + ['distance_object1_m']

    def __call__(self, fov_horizontal_deg=None, distance_object1_m=None):
        return RealWidthHelperCalc.calc_real_width(fov_horizontal_deg,
                                                  distance_object1_m)

class RealHeightObject1Calc(RealHeightHelperCalc):

    REQUIRES = RealHeightHelperCalc.REQUIRES + ['distance_object1_m']

    def __call__(self, fov_vertical_deg=None, distance_object1_m=None):
        return RealHeightHelperCalc.calc_real_height(fov_vertical_deg,
                                                     distance_object1_m)

class RealWidthObject2Calc(RealWidthHelperCalc):

    REQUIRES = RealWidthHelperCalc.REQUIRES + ['distance_object2_m']

    def __call__(self, fov_horizontal_deg=None, distance_object2_m=None):
        return RealWidthHelperCalc.calc_real_width(fov_horizontal_deg,
                                                  distance_object2_m)

class RealHeightObject2Calc(RealHeightHelperCalc):

    REQUIRES = RealHeightHelperCalc.REQUIRES + ['distance_object2_m']

    def __call__(self, fov_vertical_deg=None, distance_object2_m=None):
        return RealHeightHelperCalc.calc_real_height(fov_vertical_deg,
                                                     distance_object2_m)

class FrameWidthMMCalc(Evaluator):

    REQUIRES = [
        'frame_width_px',
        'sensor_width_px',
        'sensor_width_mm'
    ]

    def __call__(self, frame_width_px=None,
                 sensor_width_px=None, sensor_width_mm=None):
        return sensor_width_mm * frame_width_px / sensor_width_px;

class FrameHeightMMCalc(Evaluator):

    REQUIRES = [
        'frame_height_px',
        'sensor_height_px',
        'sensor_height_mm'
    ]

    def __call__(self, frame_height_px=None,
                 sensor_height_px=None, sensor_height_mm=None):
        return sensor_height_mm * frame_height_px / sensor_height_px;

class FrameDiagonalMMCalc(Evaluator):
    pass

class FrameCropHelperCalc(Evaluator):

    REF_FRAME_WIDTH_MM = 36.0
    REF_FRAME_HEIGHT_MM = 24.0

class FrameHorizontalCropCalc(FrameCropHelperCalc):

    REQUIRES = [
        'frame_width_mm'
    ]

    def __call__(self, frame_width_mm):
        return self.REF_FRAME_WIDTH_MM / frame_width_mm;

class FrameVerticalCropCalc(FrameCropHelperCalc):

    REQUIRES = [
        'frame_height_mm'
    ]

    def __call__(self, frame_height_mm):
        return self.REF_FRAME_HEIGHT_MM / frame_height_mm

class FrameDiagonalCropCalc(FrameCropHelperCalc):

    REQUIRES = [
        'frame_width_mm',
        'frame_height_mm'
    ]

    def __call__(self, frame_width_mm, frame_height_mm):

        ref_diag = DiagonalHelperCalc.calc_diag(self.REF_FRAME_WIDTH_MM,
                                                self.REF_FRAME_HEIGHT_MM)

        diag = DiagonalHelperCalc.calc_diag(frame_width_mm, frame_height_mm)

        return ref_diag / diag

class CocUmCalc(Evaluator):

    REQUIRES = [
        'coc_px',
        'sensor_width_mm',
        'sensor_width_px',
        'sensor_height_mm',
        'sensor_height_px'
    ]

    def __call__(self, coc_px=None, sensor_width_mm=None, sensor_width_px=None,
                 sensor_height_mm=None, sensor_height_px=None):

        m = min((sensor_width_mm / sensor_width_px),
                        (sensor_height_mm / sensor_height_px))

        return 1000 * coc_px * m

class ScreenDistanceCalc(Evaluator):

    REQUIRES = [
        'screen_width_m',
        'screen_distance_n'
    ]

    def __call__(self, screen_distance_n=None, screen_width_m=None):
        return screen_distance_n * screen_width_m;

class SpectatorFovHorizontalDegCalc(Evaluator):

    REQUIRES = [
        'screen_width_m',
        'screen_distance_m'
    ]

    def __call__(self, screen_width_m=None, screen_distance_m=None):
        return (180 / math.pi) * 2 * math.atan(screen_width_m / (2 * screen_distance_m))

class PerceivedPositionPercHelperCalc(Evaluator):

    REQUIRES = [
        'interpupillary_distance_mm'
    ]

    @staticmethod
    def calc_perceived_pos_perc(interpupillary_distance_mm=None, parallax_mm=None):
        return 100 * interpupillary_distance_mm / (interpupillary_distance_mm - parallax_mm)

class PerceivedPositionNearPercCalc(PerceivedPositionPercHelperCalc):

    REQUIRES = PerceivedPositionPercHelperCalc.REQUIRES + ['parallax_near_mm']

    def __call__(self, interpupillary_distance_mm=None, parallax_near_mm=None):
        return PerceivedPositionPercHelperCalc.calc_perceived_pos_perc(interpupillary_distance_mm,
                                                                  parallax_near_mm)

class PerceivedPositionScreenPercCalc(PerceivedPositionPercHelperCalc):

    REQUIRES = PerceivedPositionPercHelperCalc.REQUIRES + ['parallax_screen_mm']

    def __call__(self, interpupillary_distance_mm=None, parallax_screen_mm=None):
        return PerceivedPositionPercHelperCalc.calc_perceived_pos_perc(interpupillary_distance_mm,
                                                                  parallax_screen_mm)

class PerceivedPositionFarPercCalc(PerceivedPositionPercHelperCalc):

    REQUIRES = PerceivedPositionPercHelperCalc.REQUIRES + ['parallax_far_mm']

    def __call__(self, interpupillary_distance_mm=None, parallax_far_mm=None):
        return PerceivedPositionPercHelperCalc.calc_perceived_pos_perc(interpupillary_distance_mm,
                                                                  parallax_far_mm)

class PerceivedPositionObject1PercCalc(PerceivedPositionPercHelperCalc):

    REQUIRES = PerceivedPositionPercHelperCalc.REQUIRES + ['parallax_object1_mm']

    def __call__(self, interpupillary_distance_mm=None, parallax_object1_mm=None):
        return PerceivedPositionPercHelperCalc.calc_perceived_pos_perc(interpupillary_distance_mm,
                                                                  parallax_object1_mm)

class PerceivedPositionObject2PercCalc(PerceivedPositionPercHelperCalc):

    REQUIRES = PerceivedPositionPercHelperCalc.REQUIRES + ['parallax_object2_mm']

    def __call__(self, interpupillary_distance_mm=None, parallax_object2_mm=None):
        return PerceivedPositionPercHelperCalc.calc_perceived_pos_perc(interpupillary_distance_mm,
                                                                  parallax_object2_mm)

class PerceivedPositionMHelperCalc(Evaluator):

    REQUIRES = [
        'screen_distance_m'
    ]

    @staticmethod
    def calc_perceived_pos_m(screen_distance_m=None, perceived_pos_perc=None):
        return screen_distance_m * perceived_pos_perc / 100;

class PerceivedPositionNearMCalc(PerceivedPositionMHelperCalc):

    REQUIRES = PerceivedPositionMHelperCalc.REQUIRES + ['perceived_position_near_percent']

    def __call__(self, screen_distance_m=None, perceived_position_near_percent=None):
        return PerceivedPositionMHelperCalc.calc_perceived_pos_m(screen_distance_m,
                                                                 perceived_position_near_percent)

class PerceivedPositionScreenMCalc(PerceivedPositionMHelperCalc):

    REQUIRES = PerceivedPositionMHelperCalc.REQUIRES + ['perceived_position_screen_percent']

    def __call__(self, screen_distance_m=None, perceived_position_screen_percent=None):
        return PerceivedPositionMHelperCalc.calc_perceived_pos_m(screen_distance_m,
                                                                 perceived_position_screen_percent)

class PerceivedPositionFarMCalc(PerceivedPositionMHelperCalc):

    REQUIRES = PerceivedPositionMHelperCalc.REQUIRES + ['perceived_position_far_percent']

    def __call__(self, screen_distance_m=None, perceived_position_far_percent=None):
        return PerceivedPositionMHelperCalc.calc_perceived_pos_m(screen_distance_m,
                                                                 perceived_position_far_percent)

class PerceivedPositionObject1MCalc(PerceivedPositionMHelperCalc):

    REQUIRES = PerceivedPositionMHelperCalc.REQUIRES + ['perceived_position_object1_percent']

    def __call__(self, screen_distance_m=None, perceived_position_object1_percent=None):
        return PerceivedPositionMHelperCalc.calc_perceived_pos_m(screen_distance_m,
                                                                 perceived_position_object1_percent)

class PerceivedPositionObject2MCalc(PerceivedPositionMHelperCalc):

    REQUIRES = PerceivedPositionMHelperCalc.REQUIRES + ['perceived_position_object2_percent']

    def __call__(self, screen_distance_m=None, perceived_position_object2_percent=None):
        return PerceivedPositionMHelperCalc.calc_perceived_pos_m(screen_distance_m,
                                                                 perceived_position_object2_percent)

class ShutterUSCalc(Evaluator):

    REQUIRES = [
        'record_framerate',
        'shutter_deg'
    ]

    def __call__(self, record_framerate=None, shutter_deg=None):
        return 1000000 / record_framerate * shutter_deg / 360
