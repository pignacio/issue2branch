#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=protected-access,line-too-long,invalid-name
# pylint: disable=too-many-instance-attributes
from __future__ import absolute_import, unicode_literals

import argparse
import json
import logging

from mock import patch, sentinel
from nose.tools import eq_
from six.moves.urllib.parse import parse_qs, urlparse  # pylint: disable=import-error
import requests

from issue2branch.trackers.base import IssueTracker
from issue2branch.trackers.redmine import Redmine
from issue2branch.config import ConfigMissing

from ..utils import (
    config_from_string, TestCase, namedtuple_with_defaults, parser_exit_replace)
from .test_base import TRACKER_OPTIONS_DEFAULTS


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


REDMINE_OPTION_DEFAULTS = dict(TRACKER_OPTIONS_DEFAULTS)
REDMINE_OPTION_DEFAULTS.update({
    'mine': False,
    'version': None,
    'all': False,
    'project': None,
    'all_projects': False,
})


MockRedmineOptions = namedtuple_with_defaults('MockRedmineOptions',
                                              list(REDMINE_OPTION_DEFAULTS),
                                              defaults=REDMINE_OPTION_DEFAULTS)


class RedmineCreateTests(TestCase):
    def setUp(self):
        self.empty_config = config_from_string('')
        self.config = config_from_string('''
[redmine]
url = http://base_url
''')

    @patch.object(IssueTracker, 'create')
    def test_proxies_parent_create(self, mock_create):
        mock_create.return_value = sentinel.tracker
        tracker = Redmine.create(self.config)
        eq_(mock_create.called, True, "IssueTracker.create was not called")
        eq_(tracker, sentinel.tracker)

    def test_proxies_config_url(self):
        tracker = Redmine.create(self.config)
        eq_(tracker._base_url, "http://base_url")

    def test_create_fails_if_config_missing(self):
        self.assertRaises(ConfigMissing, Redmine.create, self.empty_config)


class GetIssueListUrlTests(TestCase):
    def setUp(self):
        self.tracker = Redmine('http://the_base_url')
        self.mock_get_limit = self.patch_object(Redmine, 'get_list_limit')
        self.mock_get_limit.return_value = 12345
        self.mock_get_project = self.patch_object(Redmine, 'get_project')
        self.mock_get_project.return_value = None
        self.no_options = MockRedmineOptions()

    def test_querystring_defaults(self):
        url = self.tracker.get_issue_list_url(sentinel.config, self.no_options)

        parsed_qs = parse_qs(urlparse(url).query)
        self.assertNotIn('assigned_to_id', parsed_qs)
        self.assertNotIn('fixed_version_id', parsed_qs)
        self.assertNotIn('status_id', parsed_qs)

    def test_limit(self):
        url = self.tracker.get_issue_list_url(sentinel.config, self.no_options)

        self.mock_get_limit.assert_called_once_with(sentinel.config,
                                                    self.no_options)
        parsed_qs = parse_qs(urlparse(url).query)
        eq_(parsed_qs['limit'], ['12345'])

    def test_mine(self):
        options = MockRedmineOptions(mine=True)
        url = self.tracker.get_issue_list_url(sentinel.config, options)

        parsed_qs = parse_qs(urlparse(url).query)
        eq_(parsed_qs['assigned_to_id'], ['me'])

    def test_version(self):
        options = MockRedmineOptions(version='v30')
        url = self.tracker.get_issue_list_url(sentinel.config, options)

        parsed_qs = parse_qs(urlparse(url).query)
        eq_(parsed_qs['fixed_version_id'], ['v30'])

    def test_all(self):
        options = MockRedmineOptions(all=True)
        url = self.tracker.get_issue_list_url(sentinel.config, options)

        parsed_qs = parse_qs(urlparse(url).query)
        eq_(parsed_qs['status_id'], ['*'])

    def test_no_project_url(self):
        url = self.tracker.get_issue_list_url(sentinel.config, self.no_options)
        eq_(url.split("?", 1)[0], 'http://the_base_url/issues.json')

    def test_project_url(self):
        self.mock_get_project.return_value = 'the_project'
        url = self.tracker.get_issue_list_url(sentinel.config, self.no_options)
        eq_(url.split("?", 1)[0],
            'http://the_base_url/projects/the_project/issues.json')

def test_redmine_parse_issue_list():
    tracker = Redmine(sentinel.url)
    issues = {
        sentinel.json_1: sentinel.issue_1,
        sentinel.json_2: sentinel.issue_2,
        sentinel.json_3: sentinel.issue_3,
    }
    json_list = list(issues)
    with patch.object(tracker, 'extract_issue') as mock_extract_issue:
        mock_extract_issue.side_effect = lambda x: issues[x]

        parsed = tracker.parse_issue_list({'issues': json_list},
                                          sentinel.config, sentinel.options)

        mock_extract_issue.assert_any_call(sentinel.json_1)
        mock_extract_issue.assert_any_call(sentinel.json_2)
        mock_extract_issue.assert_any_call(sentinel.json_3)
        eq_(parsed, [issues[x] for x in json_list])


def test_redmine_get_issue_url():
    tracker = Redmine('http://the_base_url')
    url = tracker.get_issue_url(
        'the_issue', sentinel.config, sentinel.url)
    eq_(url, 'http://the_base_url/issues/the_issue.json')


def test_redmine_parse_issue():
    tracker = Redmine('http://the_base_url')
    with patch.object(tracker, 'extract_issue') as mock_extract_issue:
        mock_extract_issue.return_value = sentinel.issue

        parsed = tracker.parse_issue({'issue': sentinel.json_issue},
                                     sentinel.config, sentinel.options)

        mock_extract_issue.assert_called_once_with(sentinel.json_issue)
        eq_(parsed, sentinel.issue)


class RedmineExtractIssueTests(TestCase):
    def setUp(self):
        self.issue_data = {
            'id': sentinel.issue_id,
            'subject': sentinel.title
        }
        self.tracker = Redmine('http://the_base_url')

    def _issue(self):
        return self.tracker.extract_issue(self.issue_data)

    def test_issue_id(self):
        eq_(self._issue().issue_id, sentinel.issue_id)

    def test_issue_title(self):
        eq_(self._issue().title, sentinel.title)

    def test_tag_default(self):
        eq_(self._issue().tag, 'Issue')

    def test_tag(self):
        self.issue_data['tracker'] = {'name': sentinel.tag}
        eq_(self._issue().tag, sentinel.tag)

    def test_parent_default(self):
        eq_(self._issue().parent, None)

    def test_parent(self):
        self.issue_data['parent'] = {'id': sentinel.parent}
        eq_(self._issue().parent, sentinel.parent)

    def test_status_default(self):
        eq_(self._issue().status, None)

    def test_status(self):
        self.issue_data['status'] = {'name': sentinel.status}
        eq_(self._issue().status, sentinel.status)

    def test_priority_default(self):
        eq_(self._issue().priority, None)

    def test_priority(self):
        self.issue_data['priority'] = {'name': sentinel.priority}
        eq_(self._issue().priority, sentinel.priority)

    def test_assignee_default(self):
        eq_(self._issue().assignee, None)

    def test_assignee(self):
        self.issue_data['assigned_to'] = {'name': sentinel.assignee}
        eq_(self._issue().assignee, sentinel.assignee)

    def test_project_default(self):
        eq_(self._issue().project, None)

    def test_project(self):
        self.issue_data['project'] = {'name': sentinel.project}
        eq_(self._issue().project, sentinel.project)

    def test_description_default(self):
        eq_(self._issue().description, None)

    def test_description(self):
        self.issue_data['description'] = sentinel.description
        eq_(self._issue().description, sentinel.description)


class TakeIssueTests(TestCase):
    def setUp(self):
        self.tracker = Redmine('http://the_base_url')
        self.config = config_from_string('''
[redmine]
assignee_id = the_assignee_id
inprogress_id = the_inprogress_id
                                         ''')
        self.mock_request = self.patch_object(self.tracker, '_request')
        self.mock_get_url = self.patch_object(self.tracker, 'get_issue_url')
        self.mock_get_url.return_value = sentinel.url

    def test_missing_inprogress_config_fails(self):
        config = config_from_string('''
[redmine]
assignee_id = 2
                                    ''')
        self.assertRaisesRegexp(ConfigMissing,
                                'Option:[\'"]inprogress_id[\'"]',
                                self.tracker.take_issue,
                                sentinel.issue, config, sentinel.options)

    def test_missing_status_config_fails(self):
        config = config_from_string('''
[redmine]
inprogress_id = 2
                                    ''')
        self.assertRaisesRegexp(ConfigMissing,
                                'Option:[\'"]assignee_id[\'"]',
                                self.tracker.take_issue,
                                sentinel.issue, config, sentinel.options)


    def test_uses_put_request(self):
        self.tracker.take_issue(sentinel.issue, self.config, sentinel.options)

        eq_(self.mock_request.called, True, '_request was not called')
        eq_(self.mock_request.call_args[0][0], requests.put)

    def test_uses_issue_url(self):
        self.tracker.take_issue(sentinel.issue, self.config, sentinel.options)

        self.mock_get_url.assert_called_once_with(sentinel.issue, self.config,
                                                  sentinel.options)
        eq_(self.mock_request.called, True, '_request was not called')
        eq_(self.mock_request.call_args[0][1], sentinel.url)

    def test_sends_payload(self):
        self.tracker.take_issue(sentinel.issue, self.config, sentinel.options)

        eq_(self.mock_request.called, True, '_request was not called')
        payload = json.loads(self.mock_request.call_args[1]['data'])
        payload = payload['issue']

        eq_(payload['status_id'], 'the_inprogress_id')
        eq_(payload['assigned_to_id'], 'the_assignee_id')

    def test_send_content_type_header(self):
        self.tracker.take_issue(sentinel.issue, self.config, sentinel.options)

        eq_(self.mock_request.called, True, '_request was not called')
        headers = self.mock_request.call_args[1]['headers']

        eq_(headers['content-type'], 'application/json')


class GetProjectTests(TestCase):
    def setUp(self):
        self.empty_config = config_from_string('')
        self.config = config_from_string('''
[redmine]
project = config_project
                                         ''')
        self.empty_options = MockRedmineOptions()
        self.options = MockRedmineOptions(project='options_project')
        self.all_projects_options = MockRedmineOptions(
            project='options_project', all_projects=True)

    def test_get_project_default_is_none(self):
        project = Redmine.get_project(self.empty_config, self.empty_options)
        eq_(project, None)

    def test_options_set_project(self):
        project = Redmine.get_project(self.empty_config, self.options)
        eq_(project, 'options_project')

    def test_config_set_project(self):
        project = Redmine.get_project(self.config, self.empty_options)
        eq_(project, 'config_project')

    def test_options_override_config(self):
        project = Redmine.get_project(self.config, self.options)
        eq_(project, 'options_project')

    def test_all_projects_override_options(self):
        project = Redmine.get_project(self.empty_config,
                                      self.all_projects_options)
        eq_(project, None)

    def test_all_projects_override_config(self):
        project = Redmine.get_project(self.config,
                                      self.all_projects_options)
        eq_(project, None)


class RedmineParseArgs(TestCase):
    def setUp(self):
        self.parser = Redmine.get_arg_parser()
        self.parser.exit = parser_exit_replace

    @patch.object(IssueTracker, 'get_arg_parser')
    def test_proxies_base_parser(self, mock_get_parser):  # pylint: disable=no-self-use
        parser = argparse.ArgumentParser()
        mock_get_parser.return_value = parser

        redmine_parser = Redmine.get_arg_parser()

        mock_get_parser.assert_called_once_with()
        eq_(redmine_parser, parser)

    def test_mine_default(self):
        options = self.parser.parse_args([])
        eq_(options.mine, False)

    def test_mine(self):
        options = self.parser.parse_args(['--mine'])
        eq_(options.mine, True)

    def test_mine_short(self):
        options = self.parser.parse_args(['-m'])
        eq_(options.mine, True)

    def test_version_default(self):
        options = self.parser.parse_args([])
        eq_(options.version, None)

    def test_version(self):
        options = self.parser.parse_args(['--version', 'the_version'])
        eq_(options.version, 'the_version')

    def test_version_short(self):
        options = self.parser.parse_args(['-v', 'the_version'])
        eq_(options.version, 'the_version')

    def test_all_default(self):
        options = self.parser.parse_args([])
        eq_(options.all, False)

    def test_all(self):
        options = self.parser.parse_args(['--all'])
        eq_(options.all, True)

    def test_all_short(self):
        options = self.parser.parse_args(['-a'])
        eq_(options.all, True)

    def test_project_default(self):
        options = self.parser.parse_args([])
        eq_(options.project, None)

    def test_project(self):
        options = self.parser.parse_args(['--project', 'the_project'])
        eq_(options.project, 'the_project')

    def test_project_short(self):
        options = self.parser.parse_args(['-p', 'the_project'])
        eq_(options.project, 'the_project')

    def test_all_projects_default(self):
        options = self.parser.parse_args([])
        eq_(options.all_projects, False)

    def test_all_projects(self):
        options = self.parser.parse_args(['--all-projects'])
        eq_(options.all_projects, True)
