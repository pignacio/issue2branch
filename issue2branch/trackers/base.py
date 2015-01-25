'''
Created on May 17, 2014

@author: ignacio
'''
from __future__ import unicode_literals


from argparse import ArgumentParser
from BeautifulSoup import BeautifulSoup
import getpass
import re
import requests

from ..repo import branch_and_move, get_branch_name


class IssueTracker(object):
    _DEFAULT_LIST_LIMIT = 40

    def __init__(self, config, base_url=None, user=None, password=None):
        self._config = config
        self._options = None
        self._user = user or self._config.get('auth', 'user', None)
        self._password = password or self._config.get('auth', 'password', None)
        if self._user:
            self._password = self._password or getpass.getpass()
        self._base_url = base_url

    def _request(self, method, url, *args, **kwargs):
        auth = (self._user, self._password) if self._user else None
        print "Requesting '{}'".format(url)
        return method(url, auth=auth, *args, **kwargs)

    def _get_issue_url(self, issue):
        return "{}/issues/{}".format(self._base_url, issue)

    def _get_issue_contents(self, issue):
        url = self._get_issue_url(issue)
        response = self._request(requests.get, url)
        if response.status_code != 200:
            raise ValueError("HTTP GET for '{}' did not return 200 but {}"
                             .format(url, response.status_code))
        if 'application/json' in response.headers['content-type']:
            return response.json()
        else:
            return BeautifulSoup(response.content)

    def _get_single_issue(self, contents):
        raise NotImplementedError()

    def get_issue_branch(self, issue):
        contents = self._get_issue_contents(issue)
        return self._get_single_issue(contents).branch()

    def get_issues(self, limit):
        raise NotImplementedError()

    @classmethod
    def from_remotes(cls, config, remotes):  # pylint: disable=unused-argument
        return None

    @classmethod
    def from_config(cls, config):
        raise NotImplementedError()

    def take_issue(self, issue):
        raise NotImplementedError()

    def parse_args(self):
        return self._get_arg_parser().parse_args()

    def _get_arg_parser(self):  # pylint: disable=no-self-use
        parser = ArgumentParser()
        parser.add_argument("issue", nargs='?',
                            help="Issue to start working on")
        parser.add_argument("-l", "--list",
                            action='store_true', default=False,
                            help="List current issues")
        parser.add_argument("--limit",
                            action='store', type=int, default=None,
                            help="Limit --list size to this value")
        parser.add_argument("-n", "--noop",
                            action='store_true', default=False,
                            help="Show branch name but don't create it")
        parser.add_argument("-t", "--take",
                            action='store_true', default=False,
                            help="Sets yourself as the assignee, if possible")
        return parser

    def _get_list_limit(self):
        if self._options.limit is None:
            limit = self._config.get('list', 'limit', self._DEFAULT_LIST_LIMIT)
        else:
            limit = self._options.limit
        if limit <= 0:
            raise ValueError("List limit must be positive: {}".format(limit))
        return limit

    def run(self):
        self._options = self.parse_args()

        if not any([self._options.issue, self._options.list]):
            raise ValueError("Must supply an issue or -l/--list")

        def _op(message, callback, *args, **kwargs):
            if self._options.noop:
                print "(noop) {}".format(message)
            else:
                print message
                callback(*args, **kwargs)

        if self._options.list:
            try:
                issues = self.get_issues(self._get_list_limit())
            except NotImplementedError:
                print ("[ERROR] Issue list is not implemented for {}"
                       .format(self.__class__))
                return
            print "Got {} issues".format(len(issues))

            issues = {issue.issue_id: issue for issue in issues}
            childs = set()

            for issue_id, issue in issues.items():
                parent = issue.parent
                if parent is not None and parent in issues:
                    issues[parent].childs[issue_id] = issue
                    childs.add(issue_id)

            for child in childs:
                del issues[child]

            self._list_issues(issues)
        else:
            print ("Getting issue title for issue: "
                   "'{}'".format(self._options.issue))
            branch = self.get_issue_branch(self._options.issue)
            print "Got branch: '{}'".format(branch)
            branch = get_branch_name(branch)
            _op("Branching '{}'".format(branch),
                branch_and_move, branch)

            if self._options.take:
                try:
                    _op("Taking issue: {}".format(self._options.issue),
                        self.take_issue, self._options.issue)
                except NotImplementedError:
                    print ("[ERROR] Issue taking is not implemented for {}"
                           .format(self.__class__))

    @classmethod
    def _list_issues(cls, issues, indent=0):
        for dummy_issue_id, issue in sorted(issues.items()):
            print "{} * {}".format("  " * indent, issue.text())
            cls._list_issues(issue.childs, indent=indent + 1)

    @staticmethod
    def _extract_or_none(json_obj, *keys):
        for key in keys:
            try:
                json_obj = json_obj[key]
            except (KeyError, TypeError):
                return None
        return json_obj


class RepoIssueTracker(IssueTracker):

    _SSH_RE = r"[^@]+@([^:]+):([^/]+)/(.+)"
    _HTTP_RE = r"https?://([^/]+)/([^/]+)/(.+)"

    def __init__(self, config, base_url, repo_user, repo_name,
                 user=None, password=None):
        IssueTracker.__init__(self, config, base_url, user, password)
        self._repo_user = repo_user
        self._repo_name = repo_name

    @classmethod
    def _from_remotes(cls, config, remotes, domain_has):
        if 'origin' in remotes:
            try:
                domain, user, repo = cls._parse(remotes['origin'])
            except ValueError:
                return None
            if domain_has is not None and domain_has in domain:
                return cls.from_config(config, repo_user=user, repo_name=repo)

    @classmethod
    def _from_parsed_url(cls, domain,  # pylint: disable=unused-argument
                         user, repo, config):
        return cls.from_config(config, repo_user=user, repo_name=repo)

    @classmethod
    def _parse(cls, remote_url):
        for regexp in [cls._SSH_RE, cls._HTTP_RE]:
            mobj = re.search(regexp, remote_url)
            if mobj:
                return mobj.groups()
        raise ValueError("Invalid url")

    @classmethod
    def _get_default_url(cls, domain, user, repo):
        return 'http://{domain}/{user}/{repo}'.format(domain=domain, user=user,
                                                      repo=repo)

    @classmethod
    def from_config(cls, config,  # pylint: disable=arguments-differ
                    repo_user=None, repo_name=None):
        raise NotImplementedError

    def take_issue(self, issue):
        IssueTracker.take_issue(self, issue)
