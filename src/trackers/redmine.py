'''
Created on May 17, 2014

@author: ignacio
'''
from trackers.base import IssueTracker
import requests
import json


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
        return {issue['id']: "{} - {}".format(
            issue['subject'],
            self._get_assignee(issue)
        ) for issue in issues}

    def _get_assignee(self, issue):
        try:
            return issue['assigned_to']['name']
        except KeyError:
            return "Not assigned"

    def take_issue(self, issue):
        inprogress_id = self._get_from_config_or_die("inprogress_id",
                                                     "In Progress status id")
        assignee_id = self._get_from_config_or_die("assignee_id",
                                                   "Assignee user id")
        payload = {'issue': {
            'status_id': inprogress_id,
            'assigned_to_id': assignee_id
        }}

        headers = {'content-type': 'application/json'}
        print "Updating issue #{}: {}".format(issue, payload)
        self._request(requests.put, self._get_issue_url(issue),
                      json.dumps(payload), headers=headers)

    def _get_from_config_or_die(self, key, description):
        try:
            return self._config[key]
        except KeyError:
            raise KeyError("Data for '{}' is missing from config. key:'{}'"
                           .format(description, key))

