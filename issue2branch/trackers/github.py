'''
Created on May 17, 2014

@author: ignacio
'''
from __future__ import absolute_import, unicode_literals, division

import json
import requests

from six.moves.urllib.parse import urlencode  # pylint: disable=import-error

from .base import RepoIssueTracker
from ..issue import Issue
from ..objects import RepoData

_VALID_TAGS = set(('bug', 'enhancement', 'documentation', 'feature',
                   'new feature'))

class Github(RepoIssueTracker):
    def get_issue_list_url(self, config, options):
        params = {
            'per_page': self.get_list_limit(config, options),
        }
        return self._api_url("repos/{}/{}/issues?{}".format(
            self.repo_user, self.repo_name, urlencode(params),
        ))

    def parse_issue_list(self, content, config, options):
        return [self.parse_issue(issue, config, options) for issue in content]


    def get_issue_url(self, issue, config, options):
        return self._api_url("repos/{}/{}/issues/{}".format(
            self.repo_user, self.repo_name, issue,
        ))

    def parse_issue(self, content, config, options):
        issue = Issue(content['number'], content['title'],
                      description=content['body'])
        issue.assignee = self.extract_or_none(content, "assignee", "login")
        issue.tag = self._first_label(self.extract_or_none(content, 'labels'),
                                      _VALID_TAGS)
        return issue

    def take_issue(self, issue, config, options):
        url = self.get_issue_url(issue, config, options)
        data = json.dumps({'assignee': self._user})
        self._request(requests.patch, url, data=data)

    @staticmethod
    def _api_url(path):
        return "https://api.github.com/{}".format(path)

    @staticmethod
    def _first_label(labels, valid_labels):
        if not labels:
            return None
        for label in labels:
            name = label['name']
            if name.lower() in valid_labels:
                return name
        return None

    @classmethod
    def _matches_domain(cls, domain):
        return 'github.com' in domain

    @classmethod
    def get_repo_data_from_config(cls, config):
        return RepoData(
            user=config.get('github', 'repo_user', None),
            name=config.get('github', 'repo_name', None),
        )
