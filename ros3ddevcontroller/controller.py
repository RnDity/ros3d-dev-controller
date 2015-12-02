"""Core Ros3D controller logic"""
from __future__ import absolute_import
import logging
import datetime
from ros3ddevcontroller.param.store import ParametersStore, ParameterSnapshotter
from ros3ddevcontroller.param.backends import FileSnapshotBackend
from ros3ddevcontroller.util import make_dir


class Controller(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.servo = None
        self.snapshots_location = None
        self.snapshots_backend = None

    def set_servo(self, servo):
        """Servo interface"""
        self.logger.debug('setting servo to %s', servo)
        self.servo = servo

    def set_snapshots_location(self, loc):
        """Set location of snapshots"""
        self.snapshots_location = loc
        make_dir(self.snapshots_location)

        # update snapshots backend
        self.snapshots_backend = FileSnapshotBackend(self.snapshots_location)

    def apply_param(self, param):
        """Apply parameter"""
        raise NotImplementedError('not implemented')

    def get_parameters(self):
        """Return a dict with all parameters in the system"""
        return ParametersStore.parameters_as_dict()

    def _record_timestamp(self):
        """Helper for updating current timestamp in parameters"""
        now = datetime.datetime.now()
        ParametersStore.set('record_date', str(now),
                            notify=False)

    def take_snapshot(self):
        """Record a snapshot of current parameter set
        :return: ID of snapshot
        """
        # record timestamp
        self._record_timestamp()

        return ParameterSnapshotter.save(self.snapshots_backend)

    def list_snapshots(self):
        """List IDs of available snapshots

        :rtype list(int):
        :return: list of snapshot IDs
        """
        snapshots = self.snapshots_backend.list_snapshots()
        self.logger.debug('snapshots: %s', snapshots)
        return snapshots

    def get_snapshot(self, snapshot_id):
        """Obtain data of snapshot `snapshot_id`. Returns a dictionary with
        parameters stored in the snapshot

        :param snapshot_id int: ID of snapshot
        :rtype dict:

        """
        self.logger.debug('load snapshot %d', snapshot_id)
        sdata = self.snapshots_backend.load(snapshot_id)
        if not sdata:
            self.logger.error('failed to load snapshot data for ID %d', snapshot_id)
        return sdata

    def delete_snapshot(self, snapshot_id):
        """Remove snapshot snapshot `snapshot_id`.

        :param snapshot_id int: ID of snapshot
        :return: ID of removed snapshot

        """
        self.logger.debug('delete snapshot %d', snapshot_id)
        return self.snapshots_backend.delete(snapshot_id)

    def delete_all(self):
        """Remove all snapshots.

        :return: list of removed snapshot IDs

        """
        return self.snapshots_backend.delete_all()
