#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from ConfigParser import SafeConfigParser
from StringIO import StringIO
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

