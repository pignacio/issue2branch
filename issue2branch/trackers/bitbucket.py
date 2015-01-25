'''
Created on May 17, 2014

@author: ignacio
'''
import urllib

import requests

from .base import RepoIssueTracker
from ..issue import Issue


class Bitbucket(RepoIssueTracker):

    def _get_single_issue(self, contents):
        issue = Issue(contents['local_id'], contents['title'])
        return issue

    @classmethod
    def from_remotes(cls, config, remotes):
        return cls._from_remotes(config, remotes, domain_has='bitbucket.org')

    @classmethod
    def _get_default_url(cls, domain, user, repo):
        return cls._api_url("repositories/{user}/{repo}".format(**locals()))

    def get_issues(self, limit):
        params = {
            'limit': self._get_list_limit()
        }
        issues = self._api_get("repositories/{}/{}/issues?{}".format(
            self._repo_user, self._repo_name, urllib.urlencode(params)
        ))
        return [self._get_single_issue(issue) for issue in issues['issues']]

    @staticmethod
    def _api_url(path):
        return "https://bitbucket.org/api/1.0/{}".format(path)

    def _api_get(self, path):
        url = self._api_url(path)
        response = self._request(requests.get, url)
        if not response.status_code == 200:
            raise ValueError("bitbucket api returned code {} != 200 for '{}'"
                             .format(response.status_code, url))
        return response.json()

    @classmethod
    def from_config(cls, config, repo_user=None, repo_name=None):
        repo_user = config.get_or_die('bitbucket', 'repo_user',
                                      default=repo_user)
        repo_name = config.get_or_die('bitbucket', 'repo_name',
                                      default=repo_name)
        base_url = cls._get_default_url("bitbucket.org", repo_user, repo_name)
        return cls(config, base_url, repo_user, repo_name)
