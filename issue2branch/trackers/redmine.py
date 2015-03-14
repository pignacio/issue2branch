'''
Created on May 17, 2014

@author: ignacio
'''
from __future__ import unicode_literals, print_function

import json
import requests

from six.moves.urllib.parse import urlencode  # pylint: disable=import-error

from .base import IssueTracker
from ..issue import Issue


class Redmine(IssueTracker):
    def __init__(self, base_url, **kwargs):
        super(Redmine, self).__init__(**kwargs)
        self._base_url = base_url

    @staticmethod
    def get_project(config, options):
        project = config.get('redmine', 'project', None)
        if options.project:
            project = options.project
        if options.all_projects:
            project = None
        return project

    def get_issue_list_url(self, config, options):
        params = {
            'limit': self.get_list_limit(config, options),
        }
        if options.mine:
            params['assigned_to_id'] = 'me'
        if options.version:
            params['fixed_version_id'] = options.version
        if options.all:
            params['status_id'] = "*"
        project = self.get_project(config, options)
        print(self._base_url)
        base_url = (self._base_url if project is None
                    else "{}/projects/{}".format(self._base_url, project))
        return "{}/issues.json?{}".format(base_url, urlencode(params))

    def parse_issue_list(self, content, config, options):
        return [self.extract_issue(issue) for issue in content['issues']]

    def get_issue_url(self, issue, config, options):
        return "{}/issues/{}.json".format(self._base_url, issue)

    def parse_issue(self, contents, config, options):
        return self.extract_issue(contents['issue'])

    def extract_issue(self, issue_data):
        issue = Issue(issue_data['id'], issue_data['subject'])
        issue.tag = self.extract_or_none(issue_data, 'tracker', 'name')
        issue.parent = self.extract_or_none(issue_data, 'parent', 'id')
        issue.status = self._get_field_name(issue_data, "status")
        issue.priority = self._get_field_name(issue_data, "priority")
        issue.assignee = self._get_field_name(issue_data, "assigned_to")
        issue.project = self.extract_or_none(issue_data, 'project', 'name')
        issue.description = self.extract_or_none(issue_data, 'description')
        return issue

    def _get_field_name(self, issue, field):
        return self.extract_or_none(issue, field, 'name')

    def take_issue(self, issue, config, options):
        inprogress_id = config.get_or_die("redmine", "inprogress_id")
        assignee_id = config.get_or_die("redmine", "assignee_id")
        payload = {'issue': {
            'status_id': inprogress_id,
            'assigned_to_id': assignee_id
        }}

        headers = {'content-type': 'application/json'}
        print("Updating issue #{}: {}".format(issue, payload))
        self._request(requests.put, self.get_issue_url(issue, config, options),
                      data=json.dumps(payload), headers=headers)

    @classmethod
    def get_arg_parser(cls):
        parser = super(Redmine, cls).get_arg_parser()
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
    def create(cls, config, remote=None, **kwargs):
        url = config.get_or_die('redmine', 'url')
        return super(Redmine, cls).create(config, base_url=url, **kwargs)
