#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""System parameters"""

from __future__ import absolute_import

from ros3ddevcontroller.param.parameter import *

SYSTEM_PARAMETERS = [
    # shot parameters
    Parameter('scene', '', str),
    Parameter('scene_description', '', str),
    Parameter('shot', '', str),
    Parameter('location', '', str),
    Parameter('notes', '', str),

    # cli parameters
    Parameter('canera_id', 'A', str),
    Parameter('record_framerate', 25, float),
    Parameter('shutter_deg', 180, float),
    Parameter('iso', 800, int),
    Parameter('filters', '', str),
    Parameter('reel_id', '001', str),
    Parameter('clip_id', '001', str),
    Parameter('take', '3', str),
    Parameter('record_date', '', str),
    Parameter('start_absolute_timecode', 0.0, float),
    Parameter('frames', 0, int),
    Parameter('rating', '', str),
    Parameter('circle', '', str),
    Parameter('script_notes', '', str),
    Parameter('camera_notes', '', str),
    Parameter('edit_notes', '', str),
    Parameter('post_notes', '', str),

    # lens & rig parameters
    Parameter('focal_length_mm', 35, float),
    Parameter('aperture', 2.0, float),
    Parameter('focus_distance_m', 5.0, float),
    Parameter('dof_near_m', 0, float, evaluated=True, evaluator=DofNearCalc),
    Parameter('dof_far_m', 0, float, evaluated=True, evaluator=DofFarCalc),
    Parameter('fov_horizontal_deg', 0, float, evaluated=True, evaluator=FovHorizontalDegCalc),
    Parameter('fov_vertical_deg', 0, float, evaluated=True, evaluator=FovVerticalDegCalc),
    Parameter('fov_diagonal_deg', 0, float, evaluated=True, evaluator=FovDiagonalDegCalc),
    Parameter('baseline_mm', 80, float),
    Parameter('convergence_deg', 0, float, evaluated=True, evaluator=ConvergenceDegCalc),
    Parameter('convergence_px', 0, float, evaluated=True, evaluator=ConvergencePxCalc),

    # scene
    Parameter('distance_near_m', 2, float),
    Parameter('distance_far_m', 6, float),
    Parameter('distance_object_m', 0, float),
    Parameter('distance_object2_m', 0, float),
    Parameter('description_near', '', str),
    Parameter('description_far', '', str),
    Parameter('description_object', '', str),
    Parameter('description_object2', '', str),
    Parameter('parallax_near_percent', 0, float, evaluated=True, evaluator=ParallaxNearPercentCalc),
    Parameter('parallax_screen_percent', 0, float, evaluated=True, evaluator=ParallaxScreenPercentCalc),
    Parameter('parallax_far_percent', 0, float, evaluated=True, evaluator=ParallaxFarPercentCalc),
    Parameter('parallax_object_percent', 0, float, evaluated=True, evaluator=ParallaxObjectPercentCalc),
    Parameter('parallax_object2_percent', 0, float, evaluated=True, evaluator=ParallaxObject2PercentCalc),
    Parameter('parallax_near_mm', 0, float, evaluated=True, evaluator=ParallaxNearMMCalc),
    Parameter('parallax_screen_mm', 0, float, evaluated=True, evaluator=ParallaxScreenMMCalc),
    Parameter('parallax_far_mm', 0, float, evaluated=True, evaluator=ParallaxFarMMCalc),
    Parameter('parallax_object_mm', 0, float, evaluated=True, evaluator=ParallaxObjectMMCalc),
    Parameter('parallax_object2_mm', 0, float, evaluated=True, evaluator=ParallaxObject2MMCalc),
    Parameter('real_width_near_m', 0, float, evaluated=True, evaluator=RealWidthNearCalc),
    Parameter('real_heigt_near_m', 0, float, evaluated=True, evaluator=RealHeightNearCalc),
    Parameter('real_width_screen_m', 0, float, evaluated=True, evaluator=RealWidthScreenCalc),
    Parameter('real_heigt_screen_m', 0, float, evaluated=True, evaluator=RealHeightScreenCalc),
    Parameter('real_width_far_m', 0, float, evaluated=True, evaluator=RealHeightFarCalc),
    Parameter('real_heigh_far_m', 0, float, evaluated=True, evaluator=RealHeightFarCalc),
    Parameter('real_width_object_m', 0, float, evaluated=True, evaluator=RealHeightObjectCalc),
    Parameter('real_heigh_object_m', 0, float, evaluated=True, evaluator=RealHeightObjectCalc),
    Parameter('real_width_object2_m', 0, float, evaluated=True, evaluator=RealHeightObject2Calc),
    Parameter('real_heigh_object2_m', 0, float, evaluated=True, evaluator=RealHeightObject2Calc),

    # camera
    Parameter('camera_type', 'RED Mysterium-X', str),
    Parameter('sensor_width_mm', 27.7, float),
    Parameter('sensor_width_px', 5120, int),
    Parameter('sensor_height_mm', 14.6, float),
    Parameter('sensor_height_px', 2700, int),
    Parameter('frame_format', '4K', str),
    Parameter('frame_width_mm', 0, float, evaluated=True, evaluator=FrameWidthMMCalc),
    Parameter('frame_width_px', 4096, int),
    Parameter('frame_height_mm', 0, float, evaluated=True, evaluator=FrameWidthMMCalc),
    Parameter('frame_height_px', 2160, int),
    Parameter('frame_diagonal_mm', 0, float, evaluated=True, evaluator=FrameDiagonalMMCalc),
    Parameter('frame_horizontal_crop', 0, float, evaluated=True, evaluator=FrameHorizontalCropCalc),
    Parameter('frame_vertical_crop', 0, float, evaluated=True, evaluator=FrameVerticalCropCalc),
    Parameter('frame_diagonal_crop', 0, float, evaluated=True, evaluator=FrameDiagonalCropCalc),
    Parameter('coc_px', 2, float),
    Parameter('coc_um', 0, float, evaluated=True, evaluator=CocUmCalc),

    # screen
    Parameter('screen_type', 'TV 50-inch', str),
    Parameter('screen_width_m', 1.08, float),
    Parameter('screen_height_m', 0.67, float),
    Parameter('screen_distance_n', 2, float),
    Parameter('screen_distance_m', 0, float, evaluated=True, evaluator=ScreenDistanceCalc),
    Parameter('interpupillary_distance_mm', 65, float),
    Parameter('spectator_fov_horizontal_deg', 0, float, evaluated=True, evaluator=SpectatorFovHorizontalDegCalc),
    Parameter('perceived_max_popout_percent', 0, float, evaluated=True, evaluator=PerceivedMaxPopoutPercCalc),
    Parameter('perceived_max_popout_m', 0, float, evaluated=True, evaluator=PerceivedMaxPopoutMCalc),

    # project
    Parameter('production_name', '', str),
    Parameter('director', '', str),
    Parameter('director_of_photography', '', str),
    Parameter('camera_operator', '', str),
    Parameter('copyright', '', str),
    Parameter('project_framerate', 25, float),
]
