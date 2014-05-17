'''
Created on May 17, 2014

@author: ignacio
'''
from trackers.base import IssueTracker


class Github(IssueTracker):

    def _get_issue_title(self, contents):
        div = contents.find(id='show_issue')
        return ("Issue " +
                " ".join(div.find('span', c).text
                         for c in ['gh-header-number', 'js-issue-title']))

    @classmethod
    def from_remotes(cls, remotes):
        return cls._from_remotes(remotes, domain_has='github.com')
