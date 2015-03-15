#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=protected-access,too-few-public-methods
from __future__ import absolute_import, unicode_literals

import logging

from nose.tools import eq_
from six.moves.configparser import SafeConfigParser  # pylint: disable=import-error

from .utils.mock import create_autospec, patch, sentinel, Mock
from .utils import TestCase, config_from_string

from issue2branch.config import Config, ConfigMissing, get_config, get_config_file


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


@patch('issue2branch.config.SafeConfigParser')
def test_config_from_filename(mock_parser):
    mock_config = create_autospec(SafeConfigParser)
    mock_parser.return_value = mock_config
    config = Config.from_filename(sentinel.filename)

    mock_parser.assert_called_once_with()
    mock_config.read.assert_called_once_with([sentinel.filename])
    eq_(config._config, mock_config)


class ConfigTestMixin(object):
    def test_get(self):
        eq_(self.config.get('section', 'key', sentinel.default), 'value')

    def test_get_missing_key(self):
        eq_(self.config.get('empty_section', 'key', sentinel.default), sentinel.default)

    def test_get_missing_section(self):
        eq_(self.config.get('no_section', 'key', sentinel.default), sentinel.default)

    def test_get_or_die(self):
        eq_(self.config.get_or_die('section', 'key'), 'value')

    def test_get_or_die_missing_key(self):
        self.assertRaisesRegexp(ConfigMissing, "Section:'empty_section', Option:'key'",
                                self.config.get_or_die, 'empty_section', 'key')

    def test_get_or_die_missing_section(self):
        self.assertRaisesRegexp(ConfigMissing, "Section:'no_section', Option:'key'",
                                self.config.get_or_die, 'no_section', 'key')

    def test_get_or_die_with_default(self):
        eq_(self.config.get_or_die('no_section', 'no_key', default=sentinel.default), sentinel.default)

    def test_get_or_die_with_none_default(self):
        self.assertRaisesRegexp(ConfigMissing, "Section:'no_section', Option:'no_key'",
                                self.config.get_or_die, 'no_section', 'no_key', default=None)


class ConfigFromStringTests(ConfigTestMixin, TestCase):
    def setUp(self):
        self.config = config_from_string('''
[section]
key = value

[empty_section]
''')


class ConfigFromSectionsTest(ConfigTestMixin, TestCase):
    def setUp(self):
        self.config = Config.from_sections({
            'section': {
                'key': 'value',
            },
            'empty_section': {},
        })


class GetWithCoerceTest(TestCase):
    def setUp(self):
        self.config = Config.from_sections({
            'section': {
                'an_int': '10',
                'not_an_int': 'xxx',
                'a_key': 'a_value',
            }
        })

    def test_good_coerce(self):
        eq_(self.config.get_or_die('section', 'an_int', coerce=int), 10)

    def test_bad_coerce(self):
        self.assertRaisesRegexp(ValueError, "section:not_an_int is not a <(type|class) 'int'>",
                                self.config.get_or_die, 'section', 'not_an_int', coerce=int)

    def test_general_coerce(self):
        mock_coerce = Mock()
        mock_coerce.return_value = sentinel.coerced

        eq_(self.config.get_or_die('section', 'a_key', coerce=mock_coerce),
            sentinel.coerced)

        mock_coerce.assert_called_once_with('a_value')

    def test_failing_coerce(self):
        mock_coerce = Mock()
        mock_coerce.side_effect = Exception()

        self.assertRaisesRegexp(ValueError, 'section:a_key is not a ',
                                self.config.get_or_die, 'section', 'a_key', coerce=mock_coerce)

        mock_coerce.assert_called_once_with('a_value')


@patch('issue2branch.config.get_config_file', autospec=True)
@patch.object(Config, 'from_filename')
def test_get_config(mock_from_file, mock_get_file):
    mock_get_file.return_value = sentinel.filename
    mock_from_file.return_value = sentinel.config

    config = get_config()

    mock_get_file.assert_called_once_with()
    mock_from_file.assert_called_once_with(sentinel.filename)
    eq_(config, sentinel.config)


class GetConfigFileTests(TestCase):
    def setUp(self):
        self.mock_git_root = self.patch('issue2branch.config.get_git_root', autospec=True)
        self.mock_os = self.patch('issue2branch.config.os', autospec=True)

        self.mock_git_root.return_value = sentinel.git_root
        self.mock_join = self.mock_os.path.join  # pylint: disable=no-member
        self.mock_join.return_value = sentinel.filename

    def test_git_but_no_environ(self):
        self.mock_os.environ = {}

        filename = get_config_file()

        self.mock_git_root.assert_called_once_with()
        self.mock_join.assert_called_once_with(sentinel.git_root, '.issue2branch.config')
        eq_(filename, sentinel.filename)

    def test_git_and_environ(self):
        self.mock_os.environ = {'ISSUE2BRANCH_CONFIG': sentinel.environ_filename}

        filename = get_config_file()

        eq_(filename, sentinel.environ_filename)

    def test_environ_and_no_git(self):
        self.mock_os.environ = {'ISSUE2BRANCH_CONFIG': sentinel.environ_filename}
        self.mock_git_root.side_effect = iter([Exception()])
        filename = get_config_file()

        eq_(filename, sentinel.environ_filename)

    def test_no_environ_and_no_git(self):
        self.mock_os.environ = {}
        self.mock_git_root.side_effect = iter([Exception("MyError")])

        self.assertRaisesRegexp(Exception, "MyError", get_config_file)


