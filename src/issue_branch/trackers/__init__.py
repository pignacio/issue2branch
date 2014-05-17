'''
Created on May 17, 2014

@author: ignacio
'''
import os
import subprocess

from config import get_config_file
from trackers.bitbucket import Bitbucket
from trackers.github import Github
from trackers.redmine import Redmine


ISSUE_TRACKERS = {
    'redmine' : Redmine,
    'github' : Github,
    'bitbucket' : Bitbucket,
}

def get_issue_tracker(config):
    if "issue_tracker" in config and "issue_tracker_url" in config:
        issue_tracker_class = ISSUE_TRACKERS[config['issue_tracker']]
        issue_tracker = issue_tracker_class(config['issue_tracker_url'],
                                            config.get('user', None),
                                            config.get('password', None))
        return issue_tracker
    else:
        # try to autodeduce issue tracker from repo remotes
        command = ['git', 'remote', '--verbose']
        proc = subprocess.Popen(command, stdout=subprocess.PIPE)
        proc.wait()
        remotes = {}
        for line in proc.stdout:
            name, url = line.split()[:2]
            remotes[name] = url

        for issue_tracker_class in ISSUE_TRACKERS.values():
            tracker = issue_tracker_class.from_remotes(remotes)
            if tracker:
                return tracker
    raise ValueError("Could not get issue tracker type/url from config/remotes. "
                     "Is the configuration file properly setup? "
                     "({})".format(get_config_file()))
