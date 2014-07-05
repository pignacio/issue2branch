'''
Created on May 17, 2014

@author: ignacio
'''
import requests
import json


from .base import RepoIssueTracker


class Github(RepoIssueTracker):

    def _get_issue_title(self, contents):
        return "Issue {} {}".format(contents['number'], contents['title'])

    def get_issues(self):
        issues = self._api_get("repos/{}/{}/issues".format(self._repo_user,
                                                           self._repo_name))
        return {issue['number']: issue['title'] for issue in issues}

    def take_issue(self, issue):
        url = self._get_issue_url(issue)
        data = json.dumps({'assignee': self._user})
        response = self._request(requests.patch, url, data=data)
        if not response.status_code == 200:
            raise ValueError("Github api returned code {} != 200 for '{}'"
                             .format(response.status_code, url))

    @classmethod
    def _get_default_url(cls, domain, user, repo):
        return cls._api_url("repos/{user}/{repo}".format(**locals()))

    @classmethod
    def from_remotes(cls, config, remotes):
        return cls._from_remotes(config, remotes, domain_has='github.com')

    @staticmethod
    def _api_url(path):
        return "https://api.github.com/{}".format(path)

    def _api_get(self, path):
        url = self._api_url(path)
        response = self._request(requests.get, url)
        if not response.status_code == 200:
            raise ValueError("Github api returned code {} != 200 for '{}'"
                             .format(response.status_code, url))
        return response.json()

    @classmethod
    def from_config(cls, config, repo_user=None, repo_name=None):
        repo_user = config.get_or_die('github', 'repo_user', default=repo_user)
        repo_name = config.get_or_die('github', 'repo_name', default=repo_name)
        base_url = cls._get_default_url("github.com", repo_user, repo_name)
        return cls(config, base_url, repo_user, repo_name)
