'''
Created on May 17, 2014

@author: ignacio
'''
import os
import subprocess

from ..config import get_config_file
from ..repo import get_remotes
from .bitbucket import Bitbucket
from .github import Github
from .redmine import Redmine


ISSUE_TRACKERS = {
    'redmine': Redmine,
    'github': Github,
    'bitbucket': Bitbucket,
}


def get_issue_tracker(config):
    tracker = config.get('main', 'tracker', None)
    remotes = get_remotes()
    if tracker:
        try:
            issue_tracker_class = ISSUE_TRACKERS[tracker]
        except KeyError:
            raise ValueError("'{}' is not a valid issue tracker"
                             .format(tracker))

        return (issue_tracker_class.from_remotes(config, remotes) or
                issue_tracker_class.from_config(config))
    else:
        # try to autodeduce issue tracker from repo remotes
        for issue_tracker_class in ISSUE_TRACKERS.values():
            tracker = issue_tracker_class.from_remotes(config, remotes)
            if tracker:
                return tracker

    raise ValueError("Could not deduce issue tracker from git remotes, nor "
                     "it was specified in the config")
