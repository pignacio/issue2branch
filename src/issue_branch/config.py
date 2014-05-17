'''
Created on May 17, 2014

@author: ignacio
'''
import os
import yaml
from git import get_git_root

CONF_FILE = '.issue_branch.config'

def get_config_file():
    git_root = get_git_root()
    return os.path.join(git_root, CONF_FILE)

def get_config():
    config_file = get_config_file()
    if not os.path.isfile(config_file):
        return {}
    with open(config_file) as fhandle:
        return yaml.load(fhandle)
