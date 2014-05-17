'''
Created on May 17, 2014

@author: ignacio
'''
import re

from BeautifulSoup import BeautifulSoup
import requests
import getpass

class IssueTracker():

    _SSH_RE = r"[^@]+@([^:]+):([^/]+)/(.+)"
    _HTTP_RE = r"https?://([^/]+)/([^/]+)/(.+)"

    def __init__(self, base_url, user=None, password=None):
        self._base_url = base_url
        self._user = user
        self._password = None
        if user:
            self._password = password if password else getpass.getpass()

    def _get_issue_url(self, issue):
        return "{}/issues/{}".format(self._base_url, issue)

    def _get_issue_contents(self, issue):
        url = self._get_issue_url(issue)
        auth = (self._user, self._password) if self._user else None
        response = requests.get(url, auth=auth)
        if response.status_code != 200:
            raise ValueError("get for '{}' did not return 200 but {}".format(url, response.status_code))
        return BeautifulSoup(response.content)

    def _get_issue_title(self, cotents):
        raise NotImplementedError()

    def get_issue_title(self, issue):
        contents = self._get_issue_contents(issue)
        return self._get_issue_title(contents)

    @classmethod
    def from_remotes(cls, remotes):
        return None

    @classmethod
    def _from_remotes(cls, remotes, domain_has):
        if 'origin' in remotes:
            parsed = cls._parse(remotes['origin'])
            if parsed:
                domain, user, repo = parsed
                if domain_has is not None and domain_has in domain:
                    return cls._from_parsed_url(domain, user, repo)

    @classmethod
    def _from_parsed_url(cls, domain, user, repo):  # pylint: disable=W0613
        base_url = 'http://{domain}/{user}/{repo}'.format(**locals())
        return cls(base_url)

    @classmethod
    def _parse(cls, remote_url):
        for regexp in [cls._SSH_RE, cls._HTTP_RE]:
            mobj = re.search(regexp, remote_url)
            if mobj:
                return mobj.groups()
        return None
