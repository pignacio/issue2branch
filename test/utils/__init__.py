#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from unittest import TestCase as UnitTestCase
import collections
import logging
import sys

from six import StringIO
from six.moves.configparser import SafeConfigParser  # pylint: disable=import-error

from .mock import patch

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
    class MockTuple(tuple_class):
        __EXCEPTION_SENTINEL = object()
        def __new__(cls, **kwargs):
            for field in kwargs:
                if not field in tuple_class._fields:
                    raise ValueError("'{}' is not a valid field for {}".format(
                        field, tuple_class))
            values = [kwargs.get(f, cls.__EXCEPTION_SENTINEL)
                      for f in tuple_class._fields]
            return tuple_class.__new__(cls, *values) #pylint: disable=star-args

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


def namedtuple_with_defaults(tuple_name, fields, defaults=None):
    defaults = defaults or {}
    tuple_class = collections.namedtuple(tuple_name, fields)
    class NamedTuple(tuple_class):  # pylint: disable=no-init,too-few-public-methods
        __defaults = defaults

        def __new__(cls, *args, **kwargs):
            if len(args) > len(tuple_class._fields):
                raise ValueError('Too many arguments for namedtuple: got {} '
                                 'instead of {}'
                                 .format(len(args), len(tuple_class._fields)))
            defaults = cls._get_defaults()
            fields_in_args = set(tuple_class._fields[:len(args)])
            kwvalues = {f: cls.__extract_value(f, kwargs, defaults)
                        for f in tuple_class._fields if f not in fields_in_args}
            if kwargs:
                raise ValueError('Unexpected argument for namedtuple: {}'
                                 .format(kwargs.popitem()[0]))
            return tuple_class.__new__(cls, *args, **kwvalues)  # pylint: disable=star-args

        @staticmethod
        def __extract_value(key, kwargs, defaults):
            try:
                return kwargs.pop(key)
            except KeyError:
                try:
                    return defaults[key]
                except KeyError:
                    raise ValueError("Missing argument for namedtuple: '{}'"
                                     .format(key))
        @classmethod
        def _get_defaults(cls):
            return cls.__defaults

    NamedTuple.__name__ = str(tuple_name)  # Prevent unicode in Python 2.x

    # Stolen from: collections.namedtuple
    # For pickling to work, the __module__ variable needs to be set to the frame
    # where the named tuple is created.  Bypass this step in environments where
    # sys._getframe is not defined (Jython for example) or sys._getframe is not
    # defined for arguments greater than 0 (IronPython).
    try:
        NamedTuple.__module__ = sys._getframe(1).f_globals.get('__name__',  # pylint: disable=protected-access
                                                               '__main__')
    except (AttributeError, ValueError):
        pass
    # /Stolen
    return NamedTuple


class ExitCalled(Exception):
    pass


def parser_exit_replace(_status, msg):
    raise ExitCalled(msg)
