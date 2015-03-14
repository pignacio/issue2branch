#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=protected-access,line-too-long,invalid-name
# pylint: disable=too-many-instance-attributes
from __future__ import absolute_import, unicode_literals

import argparse
import logging

from nose.tools import eq_
import requests

from issue2branch.trackers.base import IssueTracker, RepoIssueTracker

from ..mock_objects import MockRepoData, MockRemoteData
from ..utils import (
    config_from_string, mock_properties, TestCase, namedtuple_with_defaults,
    parser_exit_replace)
from ..utils.mock import patch, sentinel, Mock, create_autospec


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


TRACKER_OPTIONS_DEFAULTS = {
    'issue': None,
    'list': False,
    'limit': None,
    'noop': False,
    'take': None,
    'show': None
}
MockTrackerOptions = namedtuple_with_defaults('MockTrackerOptions',
                                              list(TRACKER_OPTIONS_DEFAULTS),
                                              defaults=TRACKER_OPTIONS_DEFAULTS)

class IssueTrackerRequest(TestCase):
    ''' Tests for `IssueTracker._request`. '''
    def setUp(self):
        self.patcher_getpass = patch('issue2branch.trackers.base.getpass',
                                     autospec=True)
        self.patcher_request = patch('issue2branch.trackers.base.request',
                                     autospec=True)
        self.mock_getpass = self.patcher_getpass.start()
        self.mock_request = self.patcher_request.start()

        self.mock_request.return_value = sentinel.response
        self.mock_getpass.return_value = sentinel.password

    def tearDown(self):
        self.patcher_getpass.stop()
        self.patcher_request.stop()

    def test_kwarg_proxy(self):
        tracker = IssueTracker()
        response = tracker._request(sentinel.method, sentinel.url,
                                    kwarg=sentinel.kwvalue)

        self.mock_request.assert_called_once_with(sentinel.method,
                                                  sentinel.url,
                                                  user=None, password=None,
                                                  kwarg=sentinel.kwvalue)
        eq_(response, sentinel.response)

    def test_dont_ask_for_pass_if_no_user(self):
        tracker = IssueTracker()

        response = tracker._request(sentinel.method, sentinel.url)

        self.mock_request.assert_called_once_with(sentinel.method,
                                                  sentinel.url,
                                                  user=None, password=None)
        eq_(self.mock_getpass.called, False, "getpass was called")
        eq_(response, sentinel.response)

    def test_dont_ask_for_pass_if_set_in_init(self):
        tracker = IssueTracker(user=sentinel.user, password=sentinel.password)

        response = tracker._request(sentinel.method, sentinel.url)

        self.mock_request.assert_called_once_with(sentinel.method,
                                                  sentinel.url,
                                                  user=sentinel.user,
                                                  password=sentinel.password)
        eq_(self.mock_getpass.called, False, "getpass was called")
        eq_(response, sentinel.response)

    def test_asks_once_and_only_once_for_pass(self):
        tracker = IssueTracker(user=sentinel.user)

        response = tracker._request(sentinel.method, sentinel.url)

        self.mock_request.assert_called_once_with(sentinel.method,
                                                  sentinel.url,
                                                  user=sentinel.user,
                                                  password=sentinel.password)
        self.mock_getpass.assert_called_once_with()
        eq_(response, sentinel.response)

        self.mock_request.reset_mock()
        self.mock_request.return_value = sentinel.response_two

        response = tracker._request(sentinel.method_two,
                                    sentinel.url_two)

        self.mock_request.assert_any_call(sentinel.method_two,
                                          sentinel.url_two,
                                          user=sentinel.user,
                                          password=sentinel.password)
        self.mock_getpass.assert_called_once_with()
        eq_(response, sentinel.response_two)


class IssueTrackerParsing(TestCase):
    ''' Tests for issue / issue list fetching/parsing. '''
    def setUp(self):
        self.tracker = IssueTracker()
        self.mock_get_issue_list_url = self.patch_object(self.tracker, 'get_issue_list_url')
        self.mock_parse_issue_list = self.patch_object(self.tracker, 'parse_issue_list')
        self.mock_request = self.patch_object(self.tracker, '_request')
        self.mock_get_issue_url = self.patch_object(self.tracker, 'get_issue_url')
        self.mock_parse_issue = self.patch_object(self.tracker, 'parse_issue')

        self.patcher_get_content = patch(
            'issue2branch.trackers.base.get_response_content', autospec=True)
        self.mock_get_content = self.patcher_get_content.start()

        self.mock_request.return_value = sentinel.response
        self.mock_get_content.return_value = sentinel.content

    def tearDown(self):
        self.patcher_get_content.stop()

    def test_get_issue_list(self):
        self.mock_get_issue_list_url.return_value = sentinel.list_url
        self.mock_parse_issue_list.return_value = sentinel.parsed_list

        issue_list = self.tracker.get_issue_list(sentinel.config,
                                                 sentinel.options)

        self.mock_get_issue_list_url.assert_called_once_with(
            sentinel.config, sentinel.options)
        self.mock_request.assert_called_once_with(requests.get,
                                                  sentinel.list_url)
        self.mock_get_content.assert_called_once_with(sentinel.response)
        self.mock_parse_issue_list.assert_called_once_with(sentinel.content,
                                                           sentinel.config,
                                                           sentinel.options)
        eq_(issue_list, sentinel.parsed_list)


    def test_get_issue(self):
        self.mock_get_issue_url.return_value = sentinel.issue_url
        self.mock_parse_issue.return_value = sentinel.parsed_issue

        issue = self.tracker.get_issue(sentinel.issue_id,
                                       sentinel.config, sentinel.options)

        self.mock_get_issue_url.assert_called_once_with(sentinel.issue_id,
                                                        sentinel.config,
                                                        sentinel.options)
        self.mock_request.assert_called_once_with(requests.get,
                                                  sentinel.issue_url)
        self.mock_get_content.assert_called_once_with(sentinel.response)
        self.mock_parse_issue.assert_called_once_with(sentinel.content,
                                                      sentinel.config,
                                                      sentinel.options)
        eq_(issue, sentinel.parsed_issue)



class IssueTrackerCreateTests(TestCase):
    _CONFIG = '''
[auth]
user = the_username
password = the_password
    '''

    def setUp(self):
        self.config = config_from_string(self._CONFIG)
        self.init_patcher = patch('issue2branch.trackers.base.IssueTracker.__init__', autospec=True)
        self.init_mock = self.init_patcher.start()
        self.init_mock.return_value = None

    def tearDown(self):
        self.init_patcher.stop()

    def test_create_proxies_init(self):
        tracker = IssueTracker.create(self.config)
        eq_(self.init_mock.called, True, '__init__ was not called on create')
        eq_(self.init_mock.call_args[0][0], tracker)

    def test_user_is_set_from_config(self):
        IssueTracker.create(self.config)
        eq_(self.init_mock.call_args[1]['user'], 'the_username')

    def test_password_is_set_from_config(self):
        IssueTracker.create(self.config)
        eq_(self.init_mock.call_args[1]['user'], 'the_username')

    def test_user_kwarg_overrides_config(self):
        IssueTracker.create(self.config, user=sentinel.other_username)
        eq_(self.init_mock.call_args[1]['user'], sentinel.other_username)

    def test_password_kwarg_overrides_config(self):
        IssueTracker.create(self.config,
                            password=sentinel.other_password)
        eq_(self.init_mock.call_args[1]['password'], sentinel.other_password)


class IssueTrackerParseArgs(TestCase):
    def setUp(self):
        self.parser = IssueTracker.get_arg_parser()
        self.parser.exit = parser_exit_replace

    def test_issue_default(self):
        options = self.parser.parse_args([''])
        eq_(bool(options.issue), False)

    def test_issue(self):
        options = self.parser.parse_args(['issue_id'])
        eq_(options.issue, 'issue_id')

    def test_list_default(self):
        options = self.parser.parse_args([])
        eq_(bool(options.list), False)

    def test_list(self):
        options = self.parser.parse_args(['--list'])
        eq_(bool(options.list), True)

    def test_short_list(self):
        options = self.parser.parse_args(['-l'])
        eq_(bool(options.list), True)

    def test_show_default(self):
        options = self.parser.parse_args([''])
        eq_(bool(options.show), False)

    def test_show(self):
        options = self.parser.parse_args(['--show', 'issue_id'])
        eq_(options.show, 'issue_id')

    def test_short_show(self):
        options = self.parser.parse_args(['-s', 'issue_id'])
        eq_(options.show, 'issue_id')

    def test_limit_default(self):
        options = self.parser.parse_args([])
        eq_(options.limit, None)

    def test_limit(self):
        options = self.parser.parse_args(['--limit', '10'])
        eq_(options.limit, 10)

    def test_noop_default(self):
        options = self.parser.parse_args([''])
        eq_(options.noop, False)

    def test_noop(self):
        options = self.parser.parse_args(['--noop'])
        eq_(options.noop, True)

    def test_noop_short(self):
        options = self.parser.parse_args(['-n'])
        eq_(options.noop, True)

    def test_take_default(self):
        options = self.parser.parse_args([''])
        eq_(options.take, False)

    def test_take(self):
        options = self.parser.parse_args(['--take'])
        eq_(options.take, True)

    def test_take_short(self):
        options = self.parser.parse_args(['-t'])
        eq_(options.take, True)


def test_issue_tracker_parse_args():
    parser_mock = create_autospec(argparse.ArgumentParser)
    class Tracker(IssueTracker): # pylint: disable=abstract-method,too-few-public-methods
        pass

    Tracker.get_arg_parser = Mock()
    Tracker.get_arg_parser.return_value = parser_mock
    parser_mock.parse_args.return_value = sentinel.options

    options = Tracker.parse_args()

    Tracker.get_arg_parser.assert_called_once_with()
    parser_mock.parse_args.assert_called_once_with()
    eq_(options, sentinel.options)


class IssueTrackerListLimit(TestCase):
    def setUp(self):
        self.config_limit = config_from_string('''
[list]
limit = 99
''')
        self.config_no_limit = config_from_string('')
        self.config_zero_limit = config_from_string('''
[list]
limit = 0
''')
        self.config_negative_limit = config_from_string('''
[list]
limit = -1
''')
        self.options_limit = mock_properties(limit=88)
        self.options_no_limit = mock_properties(limit=None)
        self.options_negative_limit = mock_properties(limit=-1)
        self.options_zero_limit = mock_properties(limit=0)

    @staticmethod
    def _test_limit(config, options, limit):
        eq_(IssueTracker.get_list_limit(config, options), limit)

    def _test_non_positive_limit(self, config, options):
        self.assertRaisesRegexp(ValueError, 'List limit must be positive',
                                IssueTracker.get_list_limit,
                                config, options)

    def test_limit_default(self):
        self._test_limit(self.config_no_limit, self.options_no_limit, 40)

    def test_config_overrides_default(self):
        self._test_limit(self.config_limit, self.options_no_limit, 99)

    def test_options_override_default(self):
        self._test_limit(self.config_no_limit, self.options_limit, 88)

    def test_options_override_config(self):
        self._test_limit(self.config_limit, self.options_limit, 88)

    def test_negative_option_breaks(self):
        self._test_non_positive_limit(self.config_no_limit,
                                      self.options_negative_limit)

    def test_zero_option_breaks(self):
        self._test_non_positive_limit(self.config_no_limit,
                                      self.options_zero_limit)

    def test_negative_config_breaks(self):
        self._test_non_positive_limit(self.config_negative_limit,
                                      self.options_no_limit)

    def test_zero_config_breaks(self):
        self._test_non_positive_limit(self.config_zero_limit,
                                      self.options_no_limit)


class ExtractOrNoneTests(TestCase):
    def setUp(self):
        self.data = {
            'a': 1,
            'b': {
                'a': 2
            },
        }

    def test_single_key(self):
        eq_(IssueTracker.extract_or_none(self.data, 'a'), 1)

    def test_double_key(self):
        eq_(IssueTracker.extract_or_none(self.data, 'b', 'a'), 2)

    def test_single_nonexistant_key(self):
        eq_(IssueTracker.extract_or_none(self.data, 'c'), None)

    def test_double_nonexistant_key(self):
        eq_(IssueTracker.extract_or_none(self.data, 'b', 'b'), None)


def test_issuetracker_matches_remote():
    eq_(IssueTracker.matches_remote(''), False)
    eq_(IssueTracker.matches_remote(None), False)
    eq_(IssueTracker.matches_remote(
        'git@github.com:pignacio/issue2branch'), False)
    eq_(IssueTracker.matches_remote(
        'https://www.github.com/pignacio/issue2branch'), False)


class RepoIssueTrackerCreateTests(TestCase):
    def setUp(self):
        self.config = config_from_string('')
        self.mock_parse_remote = self.patch(
            'issue2branch.trackers.base.parse_remote_url', autospec=True)

        self.mock_parse_remote.return_value = MockRemoteData(
            repo=MockRepoData(user=sentinel.remote_user, name=sentinel.remote_name))

    @patch.object(IssueTracker, 'create')
    def test_proxies_parent_create(self, mock_create):
        mock_create.return_value = sentinel.tracker

        tracker = RepoIssueTracker.create(self.config)

        eq_(mock_create.called, True, "IssueTracker.create was not called")
        eq_(mock_create.call_args[0][0], self.config)
        eq_(tracker, sentinel.tracker)

    @patch.object(RepoIssueTracker, 'get_repo_data_from_config')
    def test_loads_config_repo_data(self, mock_get_data):
        mock_get_data.return_value = MockRepoData(user=sentinel.repo_user,
                                                  name=sentinel.repo_name)

        tracker = RepoIssueTracker.create(self.config)

        mock_get_data.assert_called_once_with(self.config)
        eq_(tracker.repo_user, sentinel.repo_user)
        eq_(tracker.repo_name, sentinel.repo_name)

    def test_loads_remote_repo_data(self):
        tracker = RepoIssueTracker.create(self.config, remote=sentinel.remote)

        self.mock_parse_remote.assert_called_once_with(sentinel.remote)
        eq_(tracker.repo_user, sentinel.remote_user)
        eq_(tracker.repo_name, sentinel.remote_name)

    @patch.object(RepoIssueTracker, 'get_repo_data_from_config')
    def test_config_repo_data_overrides_remote(self, mock_get_data):
        mock_get_data.return_value = MockRepoData(user=sentinel.config_user,
                                                  name=sentinel.config_name)

        tracker = RepoIssueTracker.create(self.config, remote=sentinel.remote)

        mock_get_data.assert_called_once_with(self.config)
        self.mock_parse_remote.assert_called_once_with(sentinel.remote)
        eq_(tracker.repo_user, sentinel.config_user)
        eq_(tracker.repo_name, sentinel.config_name)

    def test_works_when_parse_remote_url_fails(self):
        self.mock_parse_remote.side_effect = iter([ValueError()])
        RepoIssueTracker.create(self.config, sentinel.remote)
        self.mock_parse_remote.assert_called_once_with(sentinel.remote)



class RepoIssueTrackerMatchesRemoteTests(TestCase):
    class SubTracker(RepoIssueTracker):  # pylint: disable=abstract-method,too-few-public-methods
        pass

    def test_none_remote_does_not_match(self):
        eq_(self.SubTracker.matches_remote(None), False)

    def test_no_remote_matches(self):
        eq_(self.SubTracker.matches_remote('http://domain/user/name'), False)
        eq_(self.SubTracker.matches_remote('https://domain/user/name'), False)
        eq_(self.SubTracker.matches_remote('git@domain:user/name'), False)

    @patch.object(SubTracker, '_matches_domain')
    @patch('issue2branch.trackers.base.parse_remote_url')
    def test_matches_if_domain_matches(self, mock_parse_remote, mock_matches_domain):
        mock_matches_domain.return_value = sentinel.matches_domain
        mock_parse_remote.return_value = MockRemoteData(domain=sentinel.domain)
        eq_(self.SubTracker.matches_remote(sentinel.remote), sentinel.matches_domain)
        mock_matches_domain.assert_called_once_with(sentinel.domain)
