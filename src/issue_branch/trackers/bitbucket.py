'''
Created on May 17, 2014

@author: ignacio
'''
from trackers.base import IssueTracker

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
