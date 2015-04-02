#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""Utility classes for Ros3D"""

import logging
import ConfigParser

class ConfigLoader(object):
    """Ros3D system configuration loader"""

    DEFAULT_PATH = '/etc/ros3d.conf'

    def __init__(self, path=None):
        self.logger = logging.getLogger(__name__)
        self.config = None
        self._load_config(path if path else ConfigLoader.DEFAULT_PATH)

    def _load_config(self, path):
        """Load configuration from file given by `path`"""
        self.config = ConfigParser.ConfigParser()

        loaded = self.config.read(path)
        if not loaded:
            self.logger.error('failed to load configuration from %s',
                              path)

    def _get(self, section, name, default=None):
        """Try to get an option from configuration. If option is not found,
        return `default`"""
        try:
            return self.config.get(section, name)
        except ConfigParser.Error:
            self.logger.exception('failed to load %s:%s, returning default %r',
                                  section, name, default)
            return default

    def get_system(self):
        """Get assigned system"""
        sys_name = self._get('common', 'system', '')
        return sys_name
