"""Controller snapshotting backends"""

from __future__ import absolute_import
from ros3ddevcontroller.param.store import ParameterSnapshotBackend
from ros3ddevcontroller.web.codec import ParameterCodec
import logging
import re
import os

class FileSnapshotBackend(ParameterSnapshotBackend):
    """Backend for saving/loading snapshots into/from plain text files
    with parameters serialized to JSON

    The files are named using [0-9]+ and are kept at the location
    identified by `location` instance attribute. Each time a snapshot
    is saved, the maximum ID of current set is determined, and the new
    snapshot gets the ID = max + 1.

    """
    def __init__(self, location):
        self.location = location
        self.logger = logging.getLogger(__name__)

    def save(self, parameters):
        """Save parameters snapshot

        :param parameters list: list of Parameter entries"""
        self.logger.debug('save snapshot at location %s', self.location)

        last_entry = self._find_last_entry()
        new_id = last_entry + 1
        # save parameters
        path = os.path.join(self.location,
                            str(new_id))
        self.logger.debug('saving snapshot to: %s', path)
        self._save_snapshot(path, parameters)
        return new_id

    def load(self, snapshot_id):
        """Retrieve snapshot data

        :param snapshot_id int: ID of snapshot
        :rtype list:
        :return: list of Parameter entries"""
        self.logger.debug('load snapshot %d', snapshot_id)

        path = self._build_snapshot_path(snapshot_id)
        if not os.path.exists(path):
            raise KeyError('snapshot {:d} not found'.format(snapshot_id))

        with open(path, 'r') as inf:
            snapshot_data = ParameterCodec(as_set=True).decode(inf.read())
        return snapshot_data

    def delete(self, snapshot_id):
        """Remove snapshot snapshot `snapshot_id`.

        :param snapshot_id int: ID of snapshot
        :return: ID of removed snapshot

        """
        self.logger.debug('delete snapshot %d', snapshot_id)

        path = self._build_snapshot_path(snapshot_id)
        if os.path.exists(path):
            os.remove(path)
        return snapshot_id

    def delete_all(self):
        """Remove all snapshots.

        :return: list of removed snapshots

        """
        self.logger.warning('remove all snapshots')
        snapshots = self._list_snapshot_ids()
        for snapshot in snapshots:
            self.delete(snapshot)
        return snapshots

    def _build_snapshot_path(self, sid):
        """Return a path to snapshot file with given ID

        :param sid int: snapshot ID"""
        return os.path.join(self.location, str(sid))

    @classmethod
    def _save_snapshot(cls, path, parameters):
        with open(path, 'w') as outf:
            outf.write(ParameterCodec(as_set=True).encode(parameters))

    def _list_snapshot_ids(self):
        snapshots = [int(en) for en in os.listdir(self.location)
                     if os.path.isfile(self._build_snapshot_path(en))
                     and re.match(r'\d+', en)]
        return snapshots

    def _find_last_entry(self):
        maybe_files = self._list_snapshot_ids()
        self.logger.debug('found snapshots: %s', maybe_files)

        max_entry = 0
        if maybe_files:
            max_entry = max(maybe_files)
        self.logger.debug('current max entry: %d', max_entry)
        return max_entry

    def list_snapshots(self):
        return sorted(self._list_snapshot_ids())
