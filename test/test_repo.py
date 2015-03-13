#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=protected-access,line-too-long,invalid-name
# pylint: disable=too-many-instance-attributes
from __future__ import absolute_import, unicode_literals

import logging
from unittest import TestCase

from nose.tools import eq_

from issue2branch.repo import parse_remote_url, get_branch_name


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class ParseRemoteTest(TestCase):
    ''' Tests for `repo.parse_remote_url. '''
    @staticmethod
    def _test_remote_url(remote_url):
        data = parse_remote_url(remote_url)
        eq_(data.domain, 'thedomain.com')
        eq_(data.repo.user, 'the_username')
        eq_(data.repo.name, 'the_name')

    def test_ssh_remote(self):
        self._test_remote_url('git@thedomain.com:the_username/the_name')

    def test_http_remote(self):
        self._test_remote_url('http://thedomain.com/the_username/the_name')

    def test_https_remote(self):
        self._test_remote_url('https://thedomain.com/the_username/the_name')

    def test_invalid_url_raises(self):
        self.assertRaisesRegexp(ValueError, 'Invalid remote url',
                                parse_remote_url, 'invalid_url')

    def test_none_argument_raises_valueerror(self):
        self.assertRaisesRegexp(ValueError, 'Invalid remote url',
                                parse_remote_url, None)


class GetBranchNameTest(TestCase):
    @staticmethod
    def _test(title, expected):
        eq_(get_branch_name(title), expected)

    def test_basic_branch(self):
        self._test(
            'Issue 3: test get branch name',
            'issue-3-test-get-branch-name')

    def test_symbols_are_deleted(self):
        self._test(
            'a:.,:;\'"?!\\/()[]{}b',
            'a-b')
