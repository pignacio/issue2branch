'''
Created on May 17, 2014

@author: ignacio
'''
from __future__ import (absolute_import, unicode_literals, division,
                        print_function)

import os
from six.moves.configparser import (  # pylint: disable=import-error
    SafeConfigParser, NoSectionError, NoOptionError
)

from .repo import get_git_root



CONF_FILE = '.issue2branch.config'
CONF_ENV_VARIABLE = 'ISSUE2BRANCH_CONFIG'


class ConfigMissing(Exception):
    def __init__(self, section, option):
        message = ("Config missing: Section:'{}', "
                   "Option:'{}'".format(section, option))
        super(ConfigMissing, self).__init__(message)


class Config(object):
    def __init__(self, config):
        self._config = config

    @classmethod
    def from_filename(cls, fname):
        print("Loading issue2branch config from: '{}'".format(fname))
        config = SafeConfigParser()
        config.read([fname])
        return cls(config)

    @classmethod
    def from_sections(cls, sections):
        config = SafeConfigParser()
        for section, keyvalues in sections.items():
            config.add_section(section)
            for key, value in keyvalues.items():
                config.set(section, key, value)
        return cls(config)


    def get(self, section, option, default, coerce=None):  # pylint: disable=redefined-builtin
        try:
            value = self._config.get(section, option)
        except (NoSectionError, NoOptionError):
            return default
        if coerce:
            try:
                value = coerce(value)
            except Exception:
                raise ValueError("Config @ {}:{} is not a {}".format(
                    section, option, coerce))
        return value

    def get_or_die(self, section, option, default=None, **kwargs):
        value = self.get(section, option, default, **kwargs)
        if value is not None:
            return value
        raise ConfigMissing(section, option)


def get_config_file():
    try:
        return os.environ[CONF_ENV_VARIABLE]
    except KeyError:
        git_root = get_git_root()
        return os.path.join(git_root, CONF_FILE)


def get_config():
    return Config.from_filename(get_config_file())
