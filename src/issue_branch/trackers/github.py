'''
Created on May 17, 2014

@author: ignacio
'''
from trackers.base import IssueTracker
import requests
import re


class Github(IssueTracker):

    def _get_issue_title(self, contents):
        div = contents.find(id='show_issue')
        return ("Issue " +
                " ".join(div.find('span', c).text
                         for c in ['gh-header-number', 'js-issue-title']))

    def get_issues(self):
        if not (self._repo_user and self._repo_name):
            raise ValueError("Could not parse repo and user from url '{}'"
                             .format(self._base_url))
        issues = _api_get("repos/{}/{}/issues".format(self._repo_user,
                                                      self._repo_name))
        return {issue['number']: issue['title'] for issue in issues}

    @classmethod
    def from_remotes(cls, remotes):
        return cls._from_remotes(remotes, domain_has='github.com')


def _api_url(path):
    return "https://api.github.com/{}".format(path)

def _api_get(path):
    url = _api_url(path)
    response = requests.get(url)
    if not response.status_code == 200:
        raise ValueError("Github api returned code {} != 200 for '{}'"
                         .format(response.status_code, url))
    return response.json()


