'''
Created on May 17, 2014

@author: ignacio
'''
import os
from ConfigParser import SafeConfigParser, NoSectionError, NoOptionError

from git import get_git_root


CONF_FILE = '.issue_branch.config'


class Config():
    def __init__(self, fname):
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
    git_root = get_git_root()
    return os.path.join(git_root, CONF_FILE)


def get_config():
    return Config(get_config_file())
