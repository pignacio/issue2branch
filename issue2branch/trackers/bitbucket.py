'''
Created on May 17, 2014

@author: ignacio
'''
from __future__ import absolute_import, unicode_literals, division

from six.moves.urllib.parse import urlencode  # pylint: disable=import-error

from .base import RepoIssueTracker, RepoData
from ..issue import Issue


class Bitbucket(RepoIssueTracker):  # pylint: disable=abstract-method
    def get_issue_list_url(self, config, options):
        params = {
            'limit': self.get_list_limit(config, options)
        }
        return self._api_url("repositories/{}/{}/issues?{}".format(
            self.repo_user, self.repo_name, urlencode(params)
        ))

    def parse_issue_list(self, content, config, options):
        return [self.parse_issue(issue, config, options)
                for issue in content['issues']]

    def parse_issue(self, content, config, options):
        issue = Issue(content['local_id'], content['title'])
        issue.description = content['content']
        return issue

    def get_issue_url(self, issue, config, options):
        return self._api_url("repositories/{}/{}/issues/{}".format(
            self.repo_user, self.repo_name, issue,
        ))

    @staticmethod
    def _api_url(path):
        return "https://bitbucket.org/api/1.0/{}".format(path)

    @classmethod
    def get_repo_data_from_config(cls, config):
        repo_user = config.get('bitbucket', 'repo_user', None)
        repo_name = config.get('bitbucket', 'repo_name', None)
        return RepoData(user=repo_user, name=repo_name)

    @classmethod
    def _matches_domain(cls, domain):
        return 'bitbucket.org' in domain
