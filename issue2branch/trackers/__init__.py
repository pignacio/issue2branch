'''
Created on May 17, 2014

@author: ignacio
'''
from __future__ import absolute_import, unicode_literals, division

import logging

from ..repo import get_remotes
from .bitbucket import Bitbucket
from .github import Github
from .redmine import Redmine


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


ISSUE_TRACKERS = {
    'redmine': Redmine,
    'github': Github,
    'bitbucket': Bitbucket,
}


def get_issue_tracker(config):
    tracker = config.get('main', 'tracker', None)
    remotes = get_remotes()
    origin = remotes.get('origin', None)
    if tracker:
        try:
            issue_tracker_class = ISSUE_TRACKERS[tracker]
        except KeyError:
            raise ValueError("'{}' is not a valid issue tracker"
                             .format(tracker))

        return issue_tracker_class.create(
            config=config,
            remote=(origin if issue_tracker_class.matches_remote(origin)
                    else None),
        )
    elif origin:
        # try to autodeduce issue tracker from repo remotes
        for issue_tracker_class in ISSUE_TRACKERS.values():
            if not issue_tracker_class.matches_remote(origin):
                logger.debug("%s did not match remotes.", issue_tracker_class)
                continue
            logger.debug("%s matched remotes. Creating...", issue_tracker_class)
            return issue_tracker_class.create(config, origin)

    raise ValueError("Could not deduce issue tracker from git remotes, nor "
                     "it was specified in the config")
