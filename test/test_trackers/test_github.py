#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=protected-access
from __future__ import absolute_import, unicode_literals

import json
import logging

from mock import patch, sentinel
from nose.tools import eq_
import requests

from ..utils import TestCase

from issue2branch.trackers.github import Github
from issue2branch.config import Config


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class GithubTests(TestCase):
    def setUp(self):
        self.tracker = Github(repo_user='repo_user', repo_name='repo_name')

    def test_get_issue_list_url(self):
        with patch.object(self.tracker, 'get_list_limit') as mock_get_limit:
            mock_get_limit.return_value = '12345'

            eq_(self.tracker.get_issue_list_url(sentinel.config, sentinel.options),
                "https://api.github.com/repos/repo_user/repo_name/issues?per_page=12345")
            mock_get_limit.assert_called_once_with(sentinel.config, sentinel.options)


    def test_parse_issue_list(self):
        objects = {
            sentinel.json_1: sentinel.issue_1,
            sentinel.json_2: sentinel.issue_2,
            sentinel.json_3: sentinel.issue_3,
        }
        json_list = list(objects)
        with patch.object(self.tracker, 'parse_issue') as mock_parse_issue:
            mock_parse_issue.side_effect = lambda x, c, o: objects[x]

            parsed = self.tracker.parse_issue_list(json_list, sentinel.config, sentinel.options)

            mock_parse_issue.assert_any_call(sentinel.json_1, sentinel.config, sentinel.options)
            mock_parse_issue.assert_any_call(sentinel.json_2, sentinel.config, sentinel.options)
            mock_parse_issue.assert_any_call(sentinel.json_3, sentinel.config, sentinel.options)
            eq_(parsed, [objects[x] for x in json_list])


    def test_get_issue_url(self):
        eq_(self.tracker.get_issue_url('the_issue', sentinel.config, sentinel.options),
            'https://api.github.com/repos/repo_user/repo_name/issues/the_issue')


class ParseIssueTests(TestCase):
    def setUp(self):
        self.tracker = Github(repo_user='repo_user', repo_name='repo_name')
        self.issue_data = {
            'number': sentinel.issue_id,
            'title': sentinel.title,
            'body': sentinel.description,
        }

    def _issue(self):
        return self.tracker.parse_issue(self.issue_data, sentinel.config, sentinel.options)

    def test_issue_id(self):
        eq_(self._issue().issue_id, sentinel.issue_id)

    def test_title(self):
        eq_(self._issue().title, sentinel.title)

    def test_description(self):
        eq_(self._issue().description, sentinel.description)

    def test_assignee_default(self):
        eq_(self._issue().assignee, None)

    def test_assignee(self):
        self.issue_data['assignee'] = {'login': sentinel.assignee}
        eq_(self._issue().assignee, sentinel.assignee)

    def test_tag_default(self):
        eq_(self._issue().tag, 'Issue')

    def test_tag_bug(self):
        self.issue_data['labels'] = [{'name': 'bug'}]
        eq_(self._issue().tag, 'bug')

    def test_tag_enhancement(self):
        self.issue_data['labels'] = [{'name': 'enhancement'}]
        eq_(self._issue().tag, 'enhancement')

    def test_tag_feature(self):
        self.issue_data['labels'] = [{'name': 'feature'}]
        eq_(self._issue().tag, 'feature')

    def test_tag_documentation(self):
        self.issue_data['labels'] = [{'name': 'documentation'}]
        eq_(self._issue().tag, 'documentation')

    def test_tag_new_feature(self):
        self.issue_data['labels'] = [{'name': 'new feature'}]
        eq_(self._issue().tag, 'new feature')

    def test_tag_invalid(self):
        self.issue_data['labels'] = [{'name': 'invalid-tag'}]
        eq_(self._issue().tag, 'Issue')

    def test_tag_multiple(self):
        self.issue_data['labels'] = [{'name': 'invalid-tag'}, {'name': 'bug'}]
        eq_(self._issue().tag, 'bug')

def test_matches_domain():
    eq_(Github._matches_domain('github.com'), True)
    eq_(Github._matches_domain('www.github.com'), True)
    eq_(Github._matches_domain('api.github.com'), True)
    eq_(Github._matches_domain('bitbucket.org'), False)
    eq_(Github._matches_domain('redmine.com'), False)


class TakeIssue(TestCase):
    def setUp(self):
        self.tracker = Github(user='the_user', password='secret',
                              repo_user='repo_user', repo_name='repo_name')
        self.mock_request = self.patch_object(self.tracker, '_request')
        self.mock_get_url = self.patch_object(self.tracker, 'get_issue_url')
        self.mock_get_url.return_value = sentinel.url

    def test_uses_http_patch(self):
        self.tracker.take_issue('the_issue', sentinel.config, sentinel.options)
        eq_(self.mock_request.called, True, '_request was not called')
        eq_(self.mock_request.call_args[0][0], requests.patch)

    def test_uses_issue_url(self):
        self.tracker.take_issue('the_issue', sentinel.config, sentinel.options)

        self.mock_get_url.assert_called_once_with('the_issue', sentinel.config, sentinel.options)
        eq_(self.mock_request.called, True, '_request was not called')
        eq_(self.mock_request.call_args[0][1], sentinel.url)

    def test_sents_correct_payload(self):
        self.tracker.take_issue('the_issue', sentinel.config, sentinel.options)

        eq_(self.mock_request.called, True, '_request was not called')
        payload = json.loads(self.mock_request.call_args[1]['data'])
        eq_(payload['assignee'], 'the_user')


class GetRepoFromConfigTests(TestCase):
    @staticmethod
    def _test_sections(sections, expected_user, expected_name):
        config = Config.from_sections(sections)
        data = Github.get_repo_data_from_config(config)
        eq_(data.user, expected_user)
        eq_(data.name, expected_name)


    def test_no_config(self):
        self._test_sections({}, None, None)

    def test_only_user(self):
        self._test_sections({'github': {'repo_user': 'the_repo_user'}},
                            'the_repo_user', None)

    def test_only_name(self):
        self._test_sections({'github': {'repo_name': 'the_repo_name'}},
                            None, 'the_repo_name')

    def test_both(self):
        self._test_sections({
            'github': {
                'repo_user': 'the_repo_user',
                'repo_name': 'the_repo_name',
            }
        }, 'the_repo_user', 'the_repo_name')
