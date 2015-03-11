#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from ConfigParser import SafeConfigParser
from StringIO import StringIO
from mock import patch
from unittest import TestCase as UnitTestCase
import collections
import logging

from issue2branch.config import Config


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


def config_from_string(value):
    config = SafeConfigParser()
    config.readfp(StringIO(value))
    return Config(config)


def mock_properties(**values):
    return collections.namedtuple('MockProperties', list(values))(**values)


class TestCase(UnitTestCase):
    def patch(self, *args, **kwargs):
        patcher = patch(*args, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def patch_object(self, *args, **kwargs):
        patcher = patch.object(*args, **kwargs)
        self.addCleanup(patcher.stop)
        return patcher.start()
