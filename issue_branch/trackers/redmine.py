'''
Created on May 17, 2014

@author: ignacio
'''
from __future__ import unicode_literals

import json
import requests
import urllib

from .. import color
from .base import IssueTracker


_PRIORITY_COLORS = {
    'Immediate': color.bright_red,
    'Urgent': color.red,
    'High': color.bright_yellow,
    'Normal': color.bright_blue,
    'Low': color.green,
}

_STATUS_COLORS = {
    'New': color.bright_yellow,
    'In Progress': color.bright_cyan,
    'Resolved': color.green,
    'Closed': color.bright_green,
}


def _format(value, format_dict):
    try:
        func = format_dict[value]
        return func(value)
    except KeyError:
        return value


class Redmine(IssueTracker):

    def _get_issue_url(self, issue):
        return IssueTracker._get_issue_url(self, issue) + ".json"

    def _get_issue_title(self, contents):
        issue = contents['issue']
        tracker = issue['tracker']['name']
        return "{} {} {}".format(tracker, issue['id'], issue['subject'])

    def get_issues(self):
        params = {
            'limit': self._config.get("redmine", "list_limit", 40)
        }
        if self._options.mine:
            params['assigned_to_id'] = 'me'
        if self._options.version:
            params['fixed_version_id'] = self._options.version
        if self._options.all:
            params['status_id'] = "*"
        url = "{}/issues.json?{}".format(self._base_url,
                                         urllib.urlencode(params))
        response = self._request(requests.get, url)
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
            status = _format(status, _STATUS_COLORS)
            priority = self._get_field_name(json_data, "priority")
            priority = _format(priority, _PRIORITY_COLORS)
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

    @staticmethod
    def _get_field_name(issue, field, default=None):
        try:
            return issue[field]['name']
        except KeyError:
            return default

    def take_issue(self, issue):
        inprogress_id = self._config.get_or_die("redmine", "inprogress_id")
        assignee_id = self._config.get_or_die("redmine", "assignee_id")
        payload = {'issue': {
            'status_id': inprogress_id,
            'assigned_to_id': assignee_id
        }}

        headers = {'content-type': 'application/json'}
        print "Updating issue #{}: {}".format(issue, payload)
        self._request(requests.put, self._get_issue_url(issue),
                      json.dumps(payload), headers=headers)

    def _get_arg_parser(self):
        parser = IssueTracker._get_arg_parser(self)
        parser.add_argument("-m", "--mine",
                            action='store_true', default=False,
                            help='Only show issues assigned to me')
        parser.add_argument("-v", "--version",
                            action='store', default=None,
                            help='Filter issue list by version')
        parser.add_argument("-a", "--all",
                            action='store_true', default=False,
                            help='Show all issues, including closed ones')
        return parser

    @classmethod
    def from_config(cls, config):
        url = config.get_or_die('redmine', 'url')
        return cls(config, url)
