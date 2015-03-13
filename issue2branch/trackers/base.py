'''
Created on May 17, 2014

@author: ignacio
'''
from __future__ import unicode_literals, print_function

from argparse import ArgumentParser
from getpass import getpass
import logging
import requests

from ..repo import branch_and_move, get_branch_name, parse_remote_url
from ..format import colorize
from ..objects import RepoData
from ..utils.requests import request, get_response_content


__all__ = ['IssueTracker', 'RepoIssueTracker']

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class IssueTracker(object):  # pylint: disable=abstract-class-little-used
    _DEFAULT_LIST_LIMIT = 40

    def __init__(self, user=None, password=None):
        self._user = user
        self._password = password

    def _ask_for_password(self):
        if not self._user:
            return
        if self._password is None:
            self._password = getpass()


    def _request(self, method, url, **kwargs):
        ''' Wrap `utils.requests.request` adding user and password. '''
        self._ask_for_password()
        return request(method, url, user=self._user, password=self._password,
                       **kwargs)

    def get_issue_list_url(self, config, options):
        raise NotImplementedError()

    def parse_issue_list(self, content, config, options):
        raise NotImplementedError()

    def get_issue_list(self, config, options):
        url = self.get_issue_list_url(config, options)
        response = self._request(requests.get, url)
        content = get_response_content(response)
        return self.parse_issue_list(content, config, options)


    def get_issue_url(self, issue, config, options):
        raise NotImplementedError()

    def parse_issue(self, content, config, options):
        raise NotImplementedError()

    def get_issue(self, issue, config, options):
        url = self.get_issue_url(issue, config, options)
        response = self._request(requests.get, url)
        content = get_response_content(response)
        return self.parse_issue(content, config, options)

    def take_issue(self, issue, config, options):
        raise NotImplementedError()

    @classmethod
    def parse_args(cls):
        return cls.get_arg_parser().parse_args()

    @classmethod
    def get_arg_parser(cls):
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
        parser.add_argument("-s", "--show",
                            default=None,
                            help="Show the issue on screen")
        return parser

    @classmethod
    def get_list_limit(cls, config, options):
        if options.limit is None:
            limit = config.get('list', 'limit', cls._DEFAULT_LIST_LIMIT,
                               coerce=int)
        else:
            limit = options.limit
        if limit <= 0:
            raise ValueError("List limit must be positive: {}".format(limit))
        return limit

    def run(self, config):
        options = self.parse_args()
        if not any([options.issue, options.list,
                    options.show]):
            raise ValueError("Must supply an issue, -s/--show or -l/--list")

        def _op(message, callback, *args, **kwargs):
            if options.noop:
                print("(noop) {}".format(message))
            else:
                print(message)
                callback(*args, **kwargs)

        if options.list:
            try:
                issues = self.get_issue_list(config, options)
            except NotImplementedError:
                print(("[ERROR] Issue list is not implemented for {}"
                       .format(self.__class__)))
                return
            print("Got {} issues".format(len(issues)))

            issues = {issue.issue_id: issue for issue in issues}
            childs = set()

            for issue_id, issue in list(issues.items()):
                parent = issue.parent
                if parent is not None and parent in issues:
                    issues[parent].childs[issue_id] = issue
                    childs.add(issue_id)

            for child in childs:
                del issues[child]

            self._list_issues(issues)
        elif options.show is not None:
            print("Showing issue {}".format(options.show))
            issue = self.get_issue(options.show, config, options)
            print()
            print("{} #{}: {}".format(colorize(issue.tag), issue.issue_id,
                                      issue.title))
            print()
            if issue.description is not None:
                print(issue.description)
            else:
                print("<No description>")
        else:
            print(("Getting issue title for issue: "
                   "'{}'".format(options.issue)))
            branch = self.get_issue(options.issue, config, options).branch()
            print("Got branch: '{}'".format(branch))
            branch = get_branch_name(branch)
            _op("Branching '{}'".format(branch),
                branch_and_move, branch)

            if options.take:
                try:
                    _op("Taking issue: {}".format(options.issue),
                        self.take_issue, options.issue, config, options)
                except NotImplementedError:
                    print(("[ERROR] Issue taking is not implemented for {}"
                           .format(self.__class__)))

    @classmethod
    def _list_issues(cls, issues, indent=0):
        for dummy_issue_id, issue in sorted(issues.items()):
            print("{} * {}".format("  " * indent, issue.text()))
            cls._list_issues(issue.childs, indent=indent + 1)

    @staticmethod
    def extract_or_none(json_obj, *keys):
        for key in keys:
            try:
                json_obj = json_obj[key]
            except (KeyError, TypeError):
                return None
        return json_obj

    @classmethod
    def matches_remote(cls, remote):  # pylint: disable=unused-argument
        return False

    @classmethod
    def create(cls, config, remote=None, **kwargs):  # pylint: disable=unused-argument
        user = kwargs.pop('user', None) or config.get('auth', 'user', None)
        password = (kwargs.pop('password', None) or
                    config.get('auth', 'password', None))
        return cls(user=user, password=password, **kwargs)


class RepoIssueTracker(IssueTracker):  # pylint: disable=abstract-method
    def __init__(self, repo_user, repo_name,
                 user=None, password=None):
        IssueTracker.__init__(self, user=user, password=password)
        self.__repo_user = repo_user
        self.__repo_name = repo_name

    @property
    def repo_user(self):
        return self.__repo_user

    @property
    def repo_name(self):
        return self.__repo_name

    @classmethod
    def _matches_domain(cls, domain):  # pylint: disable=unused-argument
        return False

    @classmethod
    def matches_remote(cls, remote):
        logger.debug("%s: matches remote: '%s'", cls, remote)
        try:
            data = parse_remote_url(remote)
        except ValueError:
            return False
        return cls._matches_domain(data.domain)

    @classmethod
    def create(cls, config, remote=None, **kwargs):
        config_data = cls.get_repo_data_from_config(config)
        try:
            remote_data = parse_remote_url(remote).repo
        except ValueError:
            remote_data = RepoData.EMPTY
        repo_user = config_data.user or remote_data.user
        repo_name = config_data.name or remote_data.name
        return super(RepoIssueTracker, cls).create(
            config, remote=remote, repo_user=repo_user, repo_name=repo_name,
            **kwargs)

    @classmethod
    def get_repo_data_from_config(cls, config):  # pylint: disable=unused-argument
        return RepoData.EMPTY
