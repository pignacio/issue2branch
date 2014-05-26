'''
Created on May 17, 2014

@author: ignacio
'''
from trackers.base import IssueTracker


class Redmine(IssueTracker):

    def _get_issue_url(self, issue):
        return IssueTracker._get_issue_url(self, issue) + ".json"

    def _get_issue_title(self, contents):
        issue = contents['issue']
        tracker = issue['tracker']['name']
        return "{} {} {}".format(tracker, issue['id'], issue['subject'])

    def get_issues(self):
        url = "{}/issues.json".format(self._base_url)
        response = self._requests_get(url)
        if response.status_code != 200:
            raise ValueError("Redmine API responded {} != 200 for '{}'"
                             .format(response.status_code, url))
        issues = response.json()['issues']
        return {issue['id']: issue['subject'] for issue in issues}
