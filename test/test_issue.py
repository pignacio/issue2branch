#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

from nose.tools import eq_

from .utils import TestCase

from issue2branch.issue import Issue


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class TextTests(TestCase):
    def setUp(self):
        self.issue = Issue('the_issue_id', 'the_issue_title')
        self.mock_colorize = self.patch('issue2branch.issue.colorize')
        self.mock_colorize.side_effect = lambda *a: ("colorize({})"
                                                     .format(",".join(a)))

    def test_default_text(self):
        eq_(self.issue.text(),
            'the_issue_id -colorize( Issue: ,Issue)the_issue_title')

    def test_priority_text(self):
        self.issue.priority = 'the_priority'
        eq_(self.issue.text(),
            'the_issue_id - [colorize(the_priority)] -colorize( Issue: ,Issue)the_issue_title')

    def test_status_text(self):
        self.issue.status = 'the_status'
        eq_(self.issue.text(),
            'the_issue_id - [colorize(the_status)] -colorize( Issue: ,Issue)the_issue_title')

    def test_priority_status_text(self):
        self.issue.status = 'the_status'
        self.issue.priority = 'the_priority'
        eq_(self.issue.text(),
            'the_issue_id - [colorize(the_priority)/colorize(the_status)] -colorize( Issue: ,Issue)the_issue_title')

    def test_assignee_text(self):
        self.issue.assignee = 'the_assignee'
        eq_(self.issue.text(),
            'the_issue_id -colorize( Issue: ,Issue)the_issue_title - \033[32m(the_assignee)\033[0m')

    def test_project_text(self):
        self.issue.project = 'the_project'
        eq_(self.issue.text(),
            'the_issue_id -\033[35m {the_project}\033[0mcolorize( Issue: ,Issue)the_issue_title')

def test_issue_branch():
    issue = Issue('the_id', 'the_title', tag='the_tag')
    eq_(issue.branch(), 'the_tag-the_id-the_title')
