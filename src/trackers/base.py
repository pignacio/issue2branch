'''
Created on May 17, 2014

@author: ignacio
'''
import re

from BeautifulSoup import BeautifulSoup
import requests
import getpass


class IssueTracker():

    def __init__(self, config, base_url, user=None, password=None):
        self._config = config
        self._base_url = base_url
        self._user = user
        self._password = None
        if user:
            self._password = password if password else getpass.getpass()

    def _requests_get(self, url):
        return self._request(requests.get, url)

    def _request(self, method, url, *args, **kwargs):
        auth = (self._user, self._password) if self._user else None
        print "Requesting '{}'".format(url)
        return method(url, auth=auth, *args, **kwargs)

    def _get_issue_url(self, issue):
        return "{}/issues/{}".format(self._base_url, issue)

    def _get_issue_contents(self, issue):
        url = self._get_issue_url(issue)
        response = self._requests_get(url)
        if response.status_code != 200:
            raise ValueError("HTTP GET for '{}' did not return 200 but {}"
                             .format(url, response.status_code))
        if 'application/json' in response.headers['content-type']:
            return response.json()
        else:
            return BeautifulSoup(response.content)

    def _get_issue_title(self, cotents):
        raise NotImplementedError()

    def get_issue_title(self, issue):
        contents = self._get_issue_contents(issue)
        return self._get_issue_title(contents)

    def get_issues(self):
        raise NotImplementedError()

    @classmethod
    def from_remotes(cls, config, remotes):
        return None

    def take_issue(self, issue):
        raise NotImplementedError()

    def parse_args(self):
        return self._get_arg_parser.parse_args()

    def _get_arg_parser(self):
        raise NotImplementedError()


class RepoIssueTracker(IssueTracker):

    _SSH_RE = r"[^@]+@([^:]+):([^/]+)/(.+)"
    _HTTP_RE = r"https?://([^/]+)/([^/]+)/(.+)"

    def __init__(self, config, base_url, user=None, password=None,
                 repo_user=None, repo_name=None):
        IssueTracker.__init__(self, config, base_url, user, password)
        self._repo_user = repo_user
        self._repo_name = repo_name

    @classmethod
    def _from_remotes(cls, config, remotes, domain_has):
        if 'origin' in remotes:
            parsed = cls._parse(remotes['origin'])
            if parsed:
                domain, user, repo = parsed
                if domain_has is not None and domain_has in domain:
                    return cls._from_parsed_url(domain, user, repo,
                                                config)

    @classmethod
    def _from_parsed_url(cls, domain, user, repo, config):
        base_url = config.get('issue_tracker_url',
                              cls._get_default_url(domain, user, repo))
        return cls(config, base_url,
                   config.get('user', None),
                   config.get('password', None),
                   repo_user=user, repo_name=repo)

    @classmethod
    def _parse(cls, remote_url):
        for regexp in [cls._SSH_RE, cls._HTTP_RE]:
            mobj = re.search(regexp, remote_url)
            if mobj:
                return mobj.groups()
        return None

    @classmethod
    def _get_default_url(cls, domain, user, repo):
        return 'http://{domain}/{user}/{repo}'.format(**locals())
