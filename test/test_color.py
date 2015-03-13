#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

from nose.tools import eq_

from issue2branch.color import *  # pylint: disable=wildcard-import

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def test_normal_colors():
    eq_(black('xxx'), '\033[30mxxx\033[0m')
    eq_(red('xxx'), '\033[31mxxx\033[0m')
    eq_(green('xxx'), '\033[32mxxx\033[0m')
    eq_(yellow('xxx'), '\033[33mxxx\033[0m')
    eq_(blue('xxx'), '\033[34mxxx\033[0m')
    eq_(magenta('xxx'), '\033[35mxxx\033[0m')
    eq_(cyan('xxx'), '\033[36mxxx\033[0m')
    eq_(white('xxx'), '\033[37mxxx\033[0m')


def test_bright_colors():
    eq_(bright_black('xxx'), '\033[30m\033[1mxxx\033[0m')
    eq_(bright_red('xxx'), '\033[31m\033[1mxxx\033[0m')
    eq_(bright_green('xxx'), '\033[32m\033[1mxxx\033[0m')
    eq_(bright_yellow('xxx'), '\033[33m\033[1mxxx\033[0m')
    eq_(bright_blue('xxx'), '\033[34m\033[1mxxx\033[0m')
    eq_(bright_magenta('xxx'), '\033[35m\033[1mxxx\033[0m')
    eq_(bright_cyan('xxx'), '\033[36m\033[1mxxx\033[0m')
    eq_(bright_white('xxx'), '\033[37m\033[1mxxx\033[0m')
