#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class _Sentinel(object):  # pylint: disable=too-few-public-methods
    def __init__(self, parent, name):
        self._parent = parent
        self._name = name

    def __repr__(self):
        return "Sentinel({id}):{parent} @ {name}".format(
            id=hex(id(self)), parent=hex(id(self._parent)), name=self._name)


class Sentinels(object):  # pylint: disable=too-few-public-methods
    def __init__(self):
        self._sentinels = {}

    def __getattribute__(self, attr):
        if attr.startswith('_'):
            return super(Sentinels, self).__getattribute__(attr)
        return self.__getitem__(attr)

    def __getitem__(self, key):
        try:
            return self._sentinels[key]
        except KeyError:
            sentinel = _Sentinel(self, key)
            self._sentinels[key] = sentinel
            return sentinel
