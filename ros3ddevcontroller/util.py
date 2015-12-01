#
# Copyright (c) 2015, Open-RnD Sp. z o.o.  All rights reserved.
#
"""Utility classes for Ros3D"""

import logging
import ConfigParser
import os.path
import os

class ConfigLoader(object):
    """Ros3D system configuration loader"""

    DEFAULT_PATH = '/etc/ros3d-controller/controller.conf'
    CONFIG_PATH = DEFAULT_PATH

    logger = logging.getLogger(__name__)

    def __init__(self, path=None):
        self.config = None
        self._load_config(path if path else self.CONFIG_PATH)

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

    def write(self):
        import tempfile
        import shutil

        fd, path = tempfile.mkstemp()
        self.logger.debug('writing config to temp file: %s', path)
        with os.fdopen(fd, 'w') as outf:
            self.config.write(outf)

        self.logger.debug('replacing %s', self.CONFIG_PATH)
        shutil.move(path, self.CONFIG_PATH)

    @classmethod
    def set_config_location(cls, path):
        cls.logger.debug('setting config path to %s', path)
        cls.CONFIG_PATH = path


class SystemConfigLoader(ConfigLoader):
    """Ros3D system configuration loader"""

    DEFAULT_PATH = '/etc/ros3d.conf'
    CONFIG_PATH = DEFAULT_PATH

    def get_system(self):
        """Get assigned system"""
        sys_name = self._get('common', 'system', '')
        return sys_name

    def set_system(self, value):
        if not self.config.has_section('common'):
            self.config.add_section('common')
        self.config.set('common', 'system', value)


def get_eth_mac():
    """Find MAC address of the first Ethernet interface. Returns either a
    string with MAC adress if the interface or 00:00:00:00:00:00.
    """
    logger = logging.getLogger(__name__)

    # root of sys-net subsystem
    sysfs_root = '/sys/class/net'

    # list interface directories
    dirs = [os.path.join(sysfs_root, d) \
            for d in os.listdir(sysfs_root)]
    if not dirs:
        return None
    dirs.sort()

    address = None
    for iface_dir in dirs:
        # read iface type
        logger.debug('checking interface %s in %s',
                     os.path.basename(iface_dir), iface_dir)

        type_file = os.path.join(iface_dir, 'type')
        with open(type_file) as inf:
            iface_type = inf.read().strip()
            logger.debug('iface type: %s', iface_type)

        # Ethernet interface has type '1'
        if iface_type != '1':
            continue

        # wifi interface also has type '1', but a phy80211 directory
        # will exist
        wifi_dir = os.path.join(iface_dir, 'phy80211')
        if os.path.exists(wifi_dir):
            logger.debug('looks like a wifi interface')
            continue

        with open(os.path.join(iface_dir, 'address')) as af:
            address = af.read().strip()
            logger.debug('eth %s MAC address: %s',
                         os.path.basename(iface_dir), address)
            break

    if not address:
        address = '00:00:00:00:00:00'

    return address
