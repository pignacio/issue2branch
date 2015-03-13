#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import collections
import logging


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


RemoteData = collections.namedtuple('RemoteData', ['domain', 'repo'])
_RepoData = collections.namedtuple('RepoData', ['user', 'name'])


class RepoData(_RepoData):  # pylint: disable=R
    EMPTY = None


RepoData.EMPTY = RepoData(None, None)


