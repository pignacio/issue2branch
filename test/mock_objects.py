#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

from .utils import mock_namedtuple_class
from issue2branch.objects import RepoData, RemoteData


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


MockRepoData = mock_namedtuple_class(RepoData)
MockRemoteData = mock_namedtuple_class(RemoteData)
