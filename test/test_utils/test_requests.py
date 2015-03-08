#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from unittest import TestCase
import logging

from mock import Mock, create_autospec, patch
from nose.tools import eq_, raises
import requests

from issue2branch.utils.requests import (
    request, get_response_content, NotOkResponse)
from ..utils import Sentinels



logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class TestRequest(TestCase):
    ''' Tests for `issue2branch.utils.requests.request`. '''
    def setUp(self):
        self.sentinels = Sentinels()
        self.method = Mock()
        self.response = create_autospec(requests.Response, status_code=200)
        self.method.return_value = self.response

    def test_no_user_proxy(self):
        response = request(self.method, self.sentinels.url,
                           kwarg=self.sentinels.kwvalue)
        self.method.assert_called_once_with(self.sentinels.url,
                                            kwarg=self.sentinels.kwvalue)
        eq_(response, self.response)


    def test_user_proxy(self):
        response = request(self.method, self.sentinels.url,
                           self.sentinels.username, self.sentinels.password,
                           kwarg=self.sentinels.kwvalue)
        self.method.assert_called_once_with(self.sentinels.url,
                                            auth=(self.sentinels.username,
                                                  self.sentinels.password),
                                            kwarg=self.sentinels.kwvalue)

    @raises(NotOkResponse)
    def test_not_found_fails(self):
        self.response.status_code = 404
        request(self.method, self.sentinels.url)

    @raises(NotOkResponse)
    def test_server_error_fails(self):
        self.response.status_code = 500
        request(self.method, self.sentinels.url)


class TestGetResponseContent(TestCase):
    ''' Tests for `issue2branch.utils.requests.get_response_content`. '''
    def setUp(self):
        self.sentinels = Sentinels()
        self.response = create_autospec(requests.Response)

    def test_parses_json(self):
        self.response.json.return_value = self.sentinels.json
        self.response.headers = {
            'content-type': 'application/json',
        }

        content = get_response_content(self.response)

        self.response.json.assert_called_once_with()
        eq_(content, self.sentinels.json)

    @patch('issue2branch.utils.requests.BeautifulSoup')
    def test_parses_html(self, mock_soup):
        self.response.content = self.sentinels.content
        self.response.headers = {
            'content-type': 'text/html',
        }
        mock_soup.return_value = self.sentinels.soup

        content = get_response_content(self.response)

        mock_soup.assert_called_once_with(self.sentinels.content)
        eq_(content, self.sentinels.soup)

    def test_parses_plain(self):
        self.response.content = self.sentinels.content
        self.response.headers = {
            'content-type': 'text/plain',
        }

        content = get_response_content(self.response)
        eq_(content, self.sentinels.content)
