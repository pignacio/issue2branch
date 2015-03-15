#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=protected-access
from __future__ import absolute_import, unicode_literals

import logging

from mock import patch, sentinel
from nose.tools import eq_

from ..utils import TestCase

from issue2branch.trackers.bitbucket import Bitbucket
from issue2branch.config import Config


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class BitbucketTests(TestCase):
    def setUp(self):
        self.tracker = Bitbucket(repo_user='repo_user', repo_name='repo_name')

    def test_get_issue_list_url(self):
        with patch.object(self.tracker, 'get_list_limit') as mock_get_limit:
            mock_get_limit.return_value = '12345'

            eq_(self.tracker.get_issue_list_url(sentinel.config, sentinel.options),
                "https://bitbucket.org/api/1.0/repositories/repo_user"
                "/repo_name/issues?limit=12345")
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

            parsed = self.tracker.parse_issue_list({'issues': json_list}, sentinel.config, sentinel.options)

            mock_parse_issue.assert_any_call(sentinel.json_1, sentinel.config, sentinel.options)
            mock_parse_issue.assert_any_call(sentinel.json_2, sentinel.config, sentinel.options)
            mock_parse_issue.assert_any_call(sentinel.json_3, sentinel.config, sentinel.options)
            eq_(parsed, [objects[x] for x in json_list])


    def test_get_issue_url(self):
        eq_(self.tracker.get_issue_url('the_issue', sentinel.config, sentinel.options),
            'https://bitbucket.org/api/1.0/repositories/repo_user/'
            'repo_name/issues/the_issue')


class ParseIssueTests(TestCase):
    def setUp(self):
        self.tracker = Bitbucket(repo_user='repo_user', repo_name='repo_name')
        self.issue_data = {
            'local_id': sentinel.issue_id,
            'title': sentinel.title,
            'content': sentinel.description,
        }

    def _issue(self):
        return self.tracker.parse_issue(self.issue_data, sentinel.config, sentinel.options)

    def test_issue_id(self):
        eq_(self._issue().issue_id, sentinel.issue_id)

    def test_title(self):
        eq_(self._issue().title, sentinel.title)

    def test_description(self):
        eq_(self._issue().description, sentinel.description)

def test_matches_domain():
    eq_(Bitbucket._matches_domain('bitbucket.org'), True)
    eq_(Bitbucket._matches_domain('www.bitbucket.org'), True)
    eq_(Bitbucket._matches_domain('github.com'), False)
    eq_(Bitbucket._matches_domain('www.github.com'), False)
    eq_(Bitbucket._matches_domain('api.github.com'), False)
    eq_(Bitbucket._matches_domain('redmine.com'), False)


class GetRepoFromConfigTests(TestCase):
    @staticmethod
    def _test_sections(sections, expected_user, expected_name):
        config = Config.from_sections(sections)
        data = Bitbucket.get_repo_data_from_config(config)
        eq_(data.user, expected_user)
        eq_(data.name, expected_name)


    def test_no_config(self):
        self._test_sections({}, None, None)

    def test_only_user(self):
        self._test_sections({'bitbucket': {'repo_user': 'the_repo_user'}},
                            'the_repo_user', None)

    def test_only_name(self):
        self._test_sections({'bitbucket': {'repo_name': 'the_repo_name'}},
                            None, 'the_repo_name')

    def test_both(self):
        self._test_sections({
            'bitbucket': {
                'repo_user': 'the_repo_user',
                'repo_name': 'the_repo_name',
            }
        }, 'the_repo_user', 'the_repo_name')
