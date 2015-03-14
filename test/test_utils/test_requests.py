#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from unittest import TestCase
import logging

from nose.tools import eq_, raises
import requests

from ..utils.mock import create_autospec, patch, sentinel

from issue2branch.utils.requests import (
    request, get_response_content, NotOkResponse)



logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class TestRequest(TestCase):
    ''' Tests for `issue2branch.utils.requests.request`. '''
    def setUp(self):
        self.method = create_autospec(requests.get)
        self.response = create_autospec(requests.Response, status_code=200)
        self.method.return_value = self.response

    def test_no_user_proxy(self):
        response = request(self.method, sentinel.url,
                           kwarg=sentinel.kwvalue)
        self.method.assert_called_once_with(sentinel.url,
                                            kwarg=sentinel.kwvalue)
        eq_(response, self.response)


    def test_user_proxy(self):
        request(self.method, sentinel.url,
                sentinel.username, sentinel.password,
                kwarg=sentinel.kwvalue)
        self.method.assert_called_once_with(sentinel.url,
                                            auth=(sentinel.username,
                                                  sentinel.password),
                                            kwarg=sentinel.kwvalue)

    @raises(NotOkResponse)
    def test_not_found_fails(self):
        self.response.status_code = 404
        request(self.method, sentinel.url)

    @raises(NotOkResponse)
    def test_server_error_fails(self):
        self.response.status_code = 500
        request(self.method, sentinel.url)

    def test_exception_contains_response(self):
        self.response.status_code = 500
        try:
            request(self.method, sentinel.url)
        except NotOkResponse as err:
            eq_(err.response, self.response)


class TestGetResponseContent(TestCase):
    ''' Tests for `issue2branch.utils.requests.get_response_content`. '''
    def setUp(self):
        self.response = create_autospec(requests.Response)

    def test_parses_json(self):
        self.response.json.return_value = sentinel.json
        self.response.headers = {
            'content-type': 'application/json',
        }

        content = get_response_content(self.response)

        self.response.json.assert_called_once_with()
        eq_(content, sentinel.json)

    @patch('issue2branch.utils.requests.BeautifulSoup')
    def test_parses_html(self, mock_soup):
        self.response.content = sentinel.content
        self.response.headers = {
            'content-type': 'text/html',
        }
        mock_soup.return_value = sentinel.soup

        content = get_response_content(self.response)

        mock_soup.assert_called_once_with(sentinel.content)
        eq_(content, sentinel.soup)

    def test_parses_plain(self):
        self.response.content = sentinel.content
        self.response.headers = {
            'content-type': 'text/plain',
        }

        content = get_response_content(self.response)
        eq_(content, sentinel.content)
