'''
Created on May 17, 2014

@author: ignacio
'''
import os
from ConfigParser import SafeConfigParser, NoSectionError, NoOptionError

from .repo import get_git_root


CONF_FILE = '.issue2branch.config'
CONF_ENV_VARIABLE = 'ISSUE2BRANCH_CONFIG'


class Config(object):
    def __init__(self, fname):
        print "Loading issue2branch config from: '{}'".format(fname)
        self._config = SafeConfigParser()
        self._config.read([fname])

    def get(self, section, option, default):
        try:
            return self._config.get(section, option)
        except (NoSectionError, NoOptionError):
            return default

    def get_or_die(self, section, option, default=None):

        try:
            return self._config.get(section, option)
        except (NoSectionError, NoOptionError):
            if default is not None:
                return default
            raise ValueError("Config missing: Section:'{}', Option:'{}'"
                             .format(section, option))


def get_config_file():
    try:
        return os.environ[CONF_ENV_VARIABLE]
    except KeyError:
        git_root = get_git_root()
        return os.path.join(git_root, CONF_FILE)


def get_config():
    return Config(get_config_file())
