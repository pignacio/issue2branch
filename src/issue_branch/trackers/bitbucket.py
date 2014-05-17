'''
Created on May 17, 2014

@author: ignacio
'''
from trackers.base import IssueTracker
import requests


class Bitbucket(IssueTracker):

    def _get_issue_title(self, contents):
        div = contents.find(id='issue-view')
        issue_id = div.find('span', "issue-id").text
        title = div.find(id='issue-title').text
        return "{} {}".format(issue_id, title)

    @classmethod
    def from_remotes(cls, remotes):
        return cls._from_remotes(remotes, domain_has='bitbucket.org')

    def _get_issue_url(self, issue):
        return "{}/issue/{}".format(self._base_url, issue)

    def get_issues(self):
        if not (self._repo_user and self._repo_name):
            raise ValueError("Could not parse repo and user from url '{}'"
                             .format(self._base_url))
        issues = _api_get("repositories/{}/{}/issues".format(self._repo_user,
                                                      self._repo_name))
        return {issue['local_id']: issue['title'] for issue in issues['issues']}


def _api_url(path):
    return "https://bitbucket.org/api/1.0/{}".format(path)

def _api_get(path):
    url = _api_url(path)
    response = requests.get(url)
    if not response.status_code == 200:
        raise ValueError("bitbucket api returned code {} != 200 for '{}'"
                         .format(response.status_code, url))
    return response.json()


