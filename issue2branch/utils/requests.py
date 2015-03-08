'''
helpers for the requests library
'''
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

from BeautifulSoup import BeautifulSoup


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class NotOkResponse(Exception):
    def __init__(self, message, response):
        super(NotOkResponse, self).__init__(message)
        self._response = response

    @property
    def response(self):
        return self._response


def request(method, url, user=None, password=None, **kwargs):
    logger.info("Requesting: %s:%s", method, url)
    if user:
        kwargs['auth'] = (user, password)
    response = method(url, **kwargs)
    logging.debug("Response status code: %s", response.status_code)
    if not 200 <= response.status_code < 300:
        raise NotOkResponse("Response status code was not 2xx: {}"
                            .format(response.status_code), response)
    return response


def get_response_content(response):
    content_type = response.headers['content-type']
    if 'application/json' in content_type:
        return response.json()
    elif 'text/html' in content_type:
        return BeautifulSoup(response.content)
    return response.content
