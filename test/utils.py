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


def mock_namedtuple_class(tuple_class):
    class MockTuple(tuple_class):  # pylint: disable=too-few-public-methods
        __EXCEPTION_SENTINEL = object()
        def __new__(cls, **kwargs):
            values = [kwargs.get(f, cls.__EXCEPTION_SENTINEL)
                      for f in tuple_class._fields]
            return tuple_class.__new__(cls, *values) # pylint: disable=star-args

        def __init__(self, **kwargs):
            for field in kwargs:
                if not field in self._fields:
                    raise ValueError("'{}' is not a valid field for {}".format(
                        field, tuple_class))
            kwargs = {f: kwargs.get(f, self.__EXCEPTION_SENTINEL)
                      for f in self._fields}
            tuple_class.__init__(self, **kwargs)

        def __getattribute__(self, attr):
            # Avoid recursion filtering _* lookups without doing self._* lookups
            value = tuple_class.__getattribute__(self, attr)
            if attr.startswith("_"):
                return value
            if value == self.__EXCEPTION_SENTINEL:
                raise AttributeError("Missing '{}' field in '{}' mock. (id={})"
                                     .format(attr, tuple_class.__name__,
                                             id(self)))
            return value
    return MockTuple


def mock_namedtuple(tuple_class, **kwargs):
    return mock_namedtuple_class(tuple_class)(**kwargs)


class ExitCalled(Exception):
    pass


def parser_exit_replace(_status, msg):
    raise ExitCalled(msg)
