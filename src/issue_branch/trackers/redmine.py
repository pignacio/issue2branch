'''
Created on May 17, 2014

@author: ignacio
'''
from trackers.base import IssueTracker

class Redmine(IssueTracker):
    def _get_issue_title(self, contents):
        content_div = contents.find(id='content')
        return "{} {}".format(content_div.h2.text, content_div.h3.text)
