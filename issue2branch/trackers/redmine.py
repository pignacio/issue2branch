'''
Created on May 17, 2014

@author: ignacio
'''
from __future__ import unicode_literals

import json
import requests
import urllib

from .base import IssueTracker
from ..issue import Issue



def _format(value, format_dict):
    try:
        func = format_dict[value]
        return func(value)
    except KeyError:
        return value


class Redmine(IssueTracker):
    def _get_issue_url(self, issue):
        return IssueTracker._get_issue_url(self, issue) + ".json"

    def _get_single_issue(self, contents):
        return self._get_issue(contents['issue'])

    def _get_issue(self, issue_data):
        issue = Issue(issue_data['id'], issue_data['subject'])
        issue.tag = self._extract_or_none(issue_data, 'tracker', 'name')
        issue.parent = self._extract_or_none(issue_data, 'parent', 'id')
        issue.status = self._get_field_name(issue_data, "status")
        issue.priority = self._get_field_name(issue_data, "priority")
        issue.assignee = self._get_field_name(issue_data, "assigned_to",
                                              None)
        issue.project = self._extract_or_none(issue_data, 'project', 'name')
        return  issue

    def _get_project(self):
        project = self._config.get('redmine', 'project', None)
        if self._options.project:
            project = self._options.project
        if self._options.all_projects:
            project = None
        return project

    def get_issues(self, limit):
        params = {
            'limit': limit,
        }
        if self._options.mine:
            params['assigned_to_id'] = 'me'
        if self._options.version:
            params['fixed_version_id'] = self._options.version
        if self._options.all:
            params['status_id'] = "*"
        project = self._get_project()
        base_url = (self._base_url if project is None
                    else "{}/projects/{}".format(self._base_url, project))
        url = "{}/issues.json?{}".format(base_url,
                                         urllib.urlencode(params))
        response = self._request(requests.get, url)
        if response.status_code != 200:
            raise ValueError("Redmine API responded {} != 200 for '{}'"
                             .format(response.status_code, url))
        issues_json = response.json()['issues']
        issues = []
        for json_data in issues_json:
            issue = self._get_issue(json_data)
            issues.append(issue)

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
        parser.add_argument("-p", "--project",
                            action='store', default=None,
                            help=('Show only issues from a given project. '
                                  'Overrides redmine.project config.'))
        parser.add_argument("--all-projects",
                            action='store_true', default=False,
                            help=('Show all projects\' issues. '
                                  'Overrides redmine.project config.'))
        return parser

    @classmethod
    def from_config(cls, config):
        url = config.get_or_die('redmine', 'url')
        return cls(config, url)
