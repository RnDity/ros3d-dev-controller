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
"""System parameters"""

from __future__ import absolute_import

from ros3ddevcontroller.param.parameter import Parameter, ReadOnlyParameter
from ros3ddevcontroller.param.evaluators import *

SERVO_PARAMETERS = [
    'baseline_mm',
    'focus_distance_m',
    'focal_length_mm',
    'aperture'
]

CAMERA_PARAMETERS = [
    'iso',
    'camera_type',
    'record_framerate',
    'shutter_us',
    'shutter_deg',
    'scene_no',
    'shot_no',
    'take_no',
    'start_absolute_timecode',
    'project_framerate',
    'director',
    'director_of_photography',
    'copyright',
    'camera_id',
    'clip_id',
    'reel_id',
    'camera_operator',
    'location',
    'frame_width_px',
    'frame_height_px',
    'frame_format',
    'camera_operator',
    'production_name',
    'record_date',
    'record_time',
    'sensor_width_mm',
    'sensor_height_mm',
    'sensor_width_px',
    'sensor_height_px'
]

SYSTEM_PARAMETERS = [
    # shot parameters
    Parameter('scene_no', '', str),
    Parameter('scene_name', '', str),
    Parameter('shot_no', '', str),
    Parameter('location', '', str),
    Parameter('notes', '', str),

    # clip parameters
    ReadOnlyParameter('camera_id', 'A', str),
    Parameter('record_framerate', 25, float),
    Parameter('shutter_deg', 180, float),
    ReadOnlyParameter('shutter_us', 20000, float, evaluator=ShutterUSCalc),
    Parameter('iso', 800, int),
    Parameter('filters', '', str),
    ReadOnlyParameter('reel_id', '001', str),
    ReadOnlyParameter('clip_id', '001', str),
    Parameter('take_no', '3', str),
    ReadOnlyParameter('record_date', '', str),
    ReadOnlyParameter('record_time', '', str),
    ReadOnlyParameter('start_absolute_timecode', '', str),
    Parameter('frames', 0, int),
    Parameter('rating', 0, int),
    Parameter('circle', False, bool),
    Parameter('script_notes', '', str),
    Parameter('camera_notes', '', str),
    Parameter('edit_notes', '', str),
    Parameter('post_notes', '', str),

    # lens & rig parameters
    ReadOnlyParameter('lens_description', '', str),
    ReadOnlyParameter('focal_length_mm', 35, float),
    ReadOnlyParameter('aperture', 2.0, float),
    ReadOnlyParameter('aperture_text', '2.0', str),
    ReadOnlyParameter('focus_distance_m', 5.0, float),
    Parameter('dof_near_m', 0, float, evaluator=DofNearCalc),
    Parameter('dof_far_m', 0, float, evaluator=DofFarCalc),
    Parameter('dof_total_m', 0, float, evaluator=DofTotalCalc),
    Parameter('fov_horizontal_deg', 0, float, evaluator=FovHorizontalDegCalc),
    Parameter('fov_vertical_deg', 0, float, evaluator=FovVerticalDegCalc),
    Parameter('fov_diagonal_deg', 0, float, evaluator=FovDiagonalDegCalc),
    Parameter('baseline_mm', 80, float),
    Parameter('convergence_deg', 0, float, evaluator=ConvergenceDegCalc),
    Parameter('convergence_px', 0, float, evaluator=ConvergencePxCalc),

    # scene
    Parameter('distance_near_m', 2, float),
    Parameter('distance_screen_m', 2, float),
    Parameter('distance_far_m', 6, float),
    Parameter('distance_object1_m', 0, float),
    Parameter('distance_object2_m', 0, float),
    Parameter('description_near', '', str),
    Parameter('description_screen', '', str),
    Parameter('description_far', '', str),
    Parameter('description_object1', '', str),
    Parameter('description_object2', '', str),
    Parameter('parallax_near_percent', 0, float, evaluator=ParallaxNearPercentCalc),
    Parameter('parallax_screen_percent', 0, float),
    Parameter('parallax_far_percent', 0, float, evaluator=ParallaxFarPercentCalc),
    Parameter('parallax_object1_percent', 0, float, evaluator=ParallaxObject1PercentCalc),
    Parameter('parallax_object2_percent', 0, float, evaluator=ParallaxObject2PercentCalc),
    Parameter('parallax_near_mm', 0, float, evaluator=ParallaxNearMMCalc),
    Parameter('parallax_screen_mm', 0, float),
    Parameter('parallax_far_mm', 0, float, evaluator=ParallaxFarMMCalc),
    Parameter('parallax_object1_mm', 0, float, evaluator=ParallaxObject1MMCalc),
    Parameter('parallax_object2_mm', 0, float, evaluator=ParallaxObject2MMCalc),
    Parameter('real_width_near_m', 0, float, evaluator=RealWidthNearCalc),
    Parameter('real_height_near_m', 0, float, evaluator=RealHeightNearCalc),
    Parameter('real_width_screen_m', 0, float, evaluator=RealWidthScreenCalc),
    Parameter('real_height_screen_m', 0, float, evaluator=RealHeightScreenCalc),
    Parameter('real_width_far_m', 0, float, evaluator=RealHeightFarCalc),
    Parameter('real_height_far_m', 0, float, evaluator=RealHeightFarCalc),
    Parameter('real_width_object1_m', 0, float, evaluator=RealWidthObject1Calc),
    Parameter('real_height_object1_m', 0, float, evaluator=RealHeightObject1Calc),
    Parameter('real_width_object2_m', 0, float, evaluator=RealWidthObject2Calc),
    Parameter('real_height_object2_m', 0, float, evaluator=RealHeightObject2Calc),

    # camera
    ReadOnlyParameter('stereoscopic_set', True, bool),
    ReadOnlyParameter('stereo_setup', 'C', str),
    ReadOnlyParameter('camera_type', 'RED Mysterium-X', str),
    ReadOnlyParameter('sensor_width_mm', 27.7, float),
    ReadOnlyParameter('sensor_width_px', 5120, int),
    ReadOnlyParameter('sensor_height_mm', 14.6, float),
    ReadOnlyParameter('sensor_height_px', 2700, int),
    Parameter('frame_format', '4K', str),
    ReadOnlyParameter('frame_width_mm', 0, float, evaluator=FrameWidthMMCalc),
    ReadOnlyParameter('frame_width_px', 4096, int),
    ReadOnlyParameter('frame_height_mm', 0, float, evaluator=FrameHeightMMCalc),
    ReadOnlyParameter('frame_height_px', 2160, int),
    ReadOnlyParameter('frame_diagonal_mm', 0, float, evaluator=FrameDiagonalMMCalc),
    ReadOnlyParameter('frame_horizontal_crop', 0, float, evaluator=FrameHorizontalCropCalc),
    ReadOnlyParameter('frame_vertical_crop', 0, float, evaluator=FrameVerticalCropCalc),
    ReadOnlyParameter('frame_diagonal_crop', 0, float, evaluator=FrameDiagonalCropCalc),
    Parameter('coc_px', 2, float),
    Parameter('coc_um', 0, float, evaluator=CocUmCalc),
    ReadOnlyParameter('record_state', 0, int),

    # integration
    Parameter('rig_controller_url', '', str),
    ReadOnlyParameter('aladin_module_enable', False, bool),
    ReadOnlyParameter('aladin_module_status', False, bool),
    ReadOnlyParameter('aladin_f_mode', 2, int),
    ReadOnlyParameter('aladin_i_mode', 2, int),
    ReadOnlyParameter('aladin_z_mode', 2, int),
    ReadOnlyParameter('aladin_c_mode', 2, int),
    ReadOnlyParameter('aladin_ia_mode', 1, int),
    ReadOnlyParameter('red_module_enable', True, bool),
    ReadOnlyParameter('red_module_status', False, bool),
    ReadOnlyParameter('phantom_module_enable', False, bool),
    ReadOnlyParameter('camera_center_hostname', '100.10.10.101', str),
    ReadOnlyParameter('camera_left_hostname', '100.10.10.101', str),
    ReadOnlyParameter('camera_right_hostname', '100.10.10.102', str),

    # screen
    Parameter('screen_type', 'TV 50-inch', str),
    Parameter('screen_width_m', 1.08, float),
    Parameter('screen_height_m', 0.67, float),
    Parameter('screen_distance_n', 2, float),
    Parameter('screen_distance_m', 0, float, evaluator=ScreenDistanceCalc),
    Parameter('interpupillary_distance_mm', 65, float),
    Parameter('spectator_fov_horizontal_deg', 0, float,
              evaluator=SpectatorFovHorizontalDegCalc),
    Parameter('perceived_position_near_percent', 0, float,
              evaluator=PerceivedPositionNearPercCalc),
    Parameter('perceived_position_screen_percent', 0, float,
              evaluator=PerceivedPositionScreenPercCalc),
    Parameter('perceived_position_far_percent', 0, float,
              evaluator=PerceivedPositionFarPercCalc),
    Parameter('perceived_position_object1_percent', 0,
              float, evaluator=PerceivedPositionObject1PercCalc),
    Parameter('perceived_position_object2_percent', 0, float,
              evaluator=PerceivedPositionObject2PercCalc),
    Parameter('perceived_position_near_m', 0, float,
              evaluator=PerceivedPositionNearMCalc),
    Parameter('perceived_position_screen_m', 0, float,
              evaluator=PerceivedPositionScreenMCalc),
    Parameter('perceived_position_far_m', 0, float,
              evaluator=PerceivedPositionFarMCalc),
    Parameter('perceived_position_object1_m', 0, float,
              evaluator=PerceivedPositionObject1MCalc),
    Parameter('perceived_position_object2_m', 0, float,
              evaluator=PerceivedPositionObject2MCalc),

    # project
    Parameter('production_name', '', str),
    Parameter('director', '', str),
    Parameter('director_of_photography', '', str),
    Parameter('camera_operator', '', str),
    Parameter('stereographer', '', str),
    ReadOnlyParameter('copyright', '', str),
    ReadOnlyParameter('project_framerate', 25, float),
]
