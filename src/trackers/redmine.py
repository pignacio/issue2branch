'''
Created on May 17, 2014

@author: ignacio
'''
from __future__ import unicode_literals
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
        issues_json = response.json()['issues']
        issues = {}
        for json_data in issues_json:
            data = {}
            try:
                data['parent'] = json_data['parent']['id']
            except KeyError:
                data['parent'] = None
            status = self._get_field_name(json_data, "status")
            priority = self._get_field_name(json_data, "priority")
            assignee = self._get_field_name(json_data, "assigned_to",
                                            "Not assigned")
            data['text'] = "[{}/{}] - {} - ({})".format(priority, status,
                                                        json_data['subject'],
                                                        assignee)
            data['childs'] = {}
            issues[json_data['id']] = data

        childs = set()

        for issue, data in issues.items():
            parent = data['parent']
            if parent is not None and parent in issues:
                issues[parent]['childs'][issue] = data
                childs.add(issue)

        for child in childs:
            del issues[child]

        return issues

    def _get_field_name(self, issue, field, default=None):
        try:
            return issue[field]['name']
        except KeyError:
            return default

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
