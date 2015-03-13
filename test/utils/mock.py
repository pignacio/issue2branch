#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name, unused-variable
from __future__ import absolute_import, unicode_literals

import logging

import six

# python version based mock module:
if six.PY2:
    import mock  # pylint: disable=unused-import
else:
    from unittest import mock  # pylint: disable=no-name-in-module,unused-import


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


create_autospec = mock.create_autospec
patch = mock.patch
sentinel = mock.sentinel
Mock = mock.Mock
MagicMock = mock.MagicMock
