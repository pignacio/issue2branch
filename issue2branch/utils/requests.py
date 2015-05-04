#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
helpers for the requests library
'''
from __future__ import absolute_import, unicode_literals, print_function

import logging
import warnings

from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecurePlatformWarning


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


__WARNED_ABOUT_PLATFORM = False


# for testing purpouses
def _reset_platform_warning():
    global __WARNED_ABOUT_PLATFORM  # pylint: disable=global-statement
    __WARNED_ABOUT_PLATFORM = False


class NotOkResponse(Exception):
    def __init__(self, message, response):
        super(NotOkResponse, self).__init__(message)
        self._response = response

    @property
    def response(self):
        return self._response


def _request(method, url, **kwargs):
    global __WARNED_ABOUT_PLATFORM  # pylint: disable=global-statement
    logger.debug("method: %s, url: %s", method, url)
    with warnings.catch_warnings(record=True) as warning_jar:
        response = method(url, **kwargs)
        logger.debug("warning_jar: %s", warning_jar)
    for warning in warning_jar:
        logger.debug('Got warning: %s', warning)
        if warning.category is InsecurePlatformWarning:
            logger.debug("Has already warned: %s", __WARNED_ABOUT_PLATFORM)
            if __WARNED_ABOUT_PLATFORM:
                continue
            print("Got an InsecurePlatformWarning. "
                  "Upgrade python to 2.7.9 or better to remove.")
            __WARNED_ABOUT_PLATFORM = True
        else:
            warnings.warn(warning.message, warning.category)
    return response


def request(method, url, user=None, password=None, **kwargs):
    logger.debug("test")
    logger.info("Requesting: %s:%s", method.__name__, url)
    if user:
        kwargs['auth'] = (user, password)
    response = _request(method, url, **kwargs)
    logger.debug("Response status code: %s", response.status_code)
    if not 200 <= response.status_code < 300:
        used_auth = bool(kwargs.get('auth', None))
        raise NotOkResponse(("Response status code for '{}' was not 2xx: {}. "
                             "Authenticated: {}").format(
                                 url, response.status_code, used_auth
                             ), response)
    return response


def get_response_content(response):
    content_type = response.headers['content-type']
    if 'application/json' in content_type:
        return response.json()
    elif 'text/html' in content_type:
        return BeautifulSoup(response.content)
    return response.content
