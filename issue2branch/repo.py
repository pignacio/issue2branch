'''
Created on May 17, 2014

@author: ignacio
'''
from __future__ import absolute_import, unicode_literals, division

import re
import os
import git

from .objects import RepoData, RemoteData


BRANCH_NAME_RE = r"[a-zA-Z0-9#]+"


def _get_repo():
    try:
        return git.Repo(".", search_parent_directories=True)
    except git.exc.InvalidGitRepositoryError:
        raise ValueError("Current directory '{}' does not belong to a git "
                         "repository".format(os.path.abspath(".")))


def get_git_root():
    return _get_repo().working_dir


def get_remotes():
    return {r.name: r.url for r in _get_repo().remotes}


def branch_and_move(branch):
    try:
        _get_repo().heads[branch].checkout()
    except IndexError:  # Branch does not exist
        _get_repo().create_head(branch).checkout()


def get_branch_name(title):
    return "-".join(re.findall(BRANCH_NAME_RE, title)).lower()


_SSH_RE = r"[^@]+@([^:]+):([^/]+)/(.+)"
_HTTP_RE = r"https?://([^/]+)/([^/]+)/(.+)"


def parse_remote_url(remote_url):
    if remote_url is None:
        raise ValueError("Invalid remote url: '{}'".format(remote_url))
    for regexp in [_SSH_RE, _HTTP_RE]:
        mobj = re.search(regexp, remote_url)
        if mobj:
            domain, user, name = mobj.groups()
            return RemoteData(domain=domain, repo=RepoData(user=user,
                                                           name=name))
    raise ValueError("Invalid remote url: '{}'".format(remote_url))
