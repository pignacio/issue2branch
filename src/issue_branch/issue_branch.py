#!/usr/bin/env python
import getpass
import os
import re
import requests
import subprocess
import sys
import yaml
from BeautifulSoup import BeautifulSoup


BRANCH_NAME_RE = "[a-zA-Z0-9\s\-_]"

CONF_FILE = '.issue_branch.config'

class IssueTracker():
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
        response = requests.get(url, auth=(self._user, self._password))
        if response.status_code != 200:
            raise ValueError("get for '{}' did not return 200 but {}".format(url, response.status_code))
        return BeautifulSoup(response.content)

    def _get_issue_title(self, cotents):
        raise NotImplementedError()

    def get_issue_title(self, issue):
        contents = self._get_issue_contents(issue)
        return self._get_issue_title(contents)

class Redmine(IssueTracker):
    def _get_issue_title(self, contents):
        content_div = contents.find(id='content')
        return "{} {}".format(content_div.h2.text, content_div.h3.text)

class Github(IssueTracker):
    def _get_issue_title(self, contents):
        div = contents.find(id='show_issue')
        return "Issue " + " ".join(div.find('span', c).text for c in ['gh-header-number', 'js-issue-title'])

ISSUE_TRACKERS = {
    'redmine' : Redmine,
    'github' : Github,
}

def _get_git_root():
    command = ['git', 'rev-parse', '--show-toplevel']
    proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    proc.wait()

    if proc.poll():
        raise ValueError("Could not get git root directory. Is this a git repo?")
    return proc.stdout.readline().strip()

def _get_config():
    git_root = _get_git_root()
    config_file = os.path.join(git_root, CONF_FILE)
    with open(config_file) as fhandle:
        return yaml.load(fhandle)

def _get_issue_tracker(config):
    issue_tracker_class = ISSUE_TRACKERS[config['issue_tracker']]
    issue_tracker = issue_tracker_class(config['issue_tracker_url'],
                                        config.get('user', None),
                                        config.get('password', None))
    return issue_tracker

def main():
    if len(sys.argv) < 2:
        raise ValueError("No issue supplied")
    issue = sys.argv[1]
    config = _get_config()
    tracker = _get_issue_tracker(config)

    title = tracker.get_issue_title(issue)
    print "Got title: '{}'".format(title)
    branch = re.sub("\s+", "-", "".join(re.findall(BRANCH_NAME_RE, title)).lower())

    print "Branching '{}'".format(branch)

    os.system("git checkout -b {}".format(branch))

if __name__ == "__main__":
    main()
