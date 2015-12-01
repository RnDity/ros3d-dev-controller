"""Core Ros3D controller logic"""
from __future__ import absolute_import
import logging
from ros3ddevcontroller.param import ParametersStore
from ros3ddevcontroller.util import make_dir


class Controller(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.servo = None
        self.snapshots_location = None

    def set_servo(self, servo):
        """Servo interface"""
        self.servo = servo

    def set_snapshots_location(self, loc):
        """Set location of snapshots"""
        self.snapshots_location = loc
        make_dir(self.snapshots_location)

    def apply_param(self, param):
        """Apply parameter"""
        raise NotImplementedError('not implemented')

    def get_params(self):
        """Return a dict with all parameters in the system"""
        return ParametersStore.parameters_as_dict()

    def take_snapshot(self):
        raise NotImplementedError('not implemented')

    def list_snapshots(self):
        raise NotImplementedError('not implemented')

