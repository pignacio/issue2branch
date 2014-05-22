#!/usr/bin/env python
import re

from config import get_config
from trackers import get_issue_tracker
from argparse import ArgumentParser
from git import branch_and_move


BRANCH_NAME_RE = r"[a-zA-Z0-9#.]+"


def _get_arg_parser():
    parser = ArgumentParser()
    parser.add_argument("issue", nargs='?',
                        help="Issue to start working on")
    parser.add_argument("-l", "--list",
                        action='store_true', default=False,
                        help="List current issues")
    parser.add_argument("-n", "--noop",
                        action='store_true', default=False,
                        help="Show branch name but don't create it")
    return parser


def _parse_args():
    parser = _get_arg_parser()
    options = parser.parse_args()
    if not options.list and options.issue is None:
        raise ValueError("Must supply --list or a issue")
    return options


def main():
    options = _parse_args()
    config = get_config()
    tracker = get_issue_tracker(config)
    if options.list:
        try:
            issues = tracker.get_issues()
        except NotImplementedError:
            print ("[ERROR] Issue list is not implemented for {}"
                   .format(tracker.__class__))
            return
        print "Got {} issues".format(len(issues))
        for issue_id, text in sorted(issues.items()):
            print " * {} - {}".format(issue_id, text)
    else:
        print "Getting issue title for issue: '{}'".format(options.issue)
        title = tracker.get_issue_title(options.issue)
        print "Got title: '{}'".format(title)
        branch = "-".join(re.findall(BRANCH_NAME_RE, title)).lower()
        if options.noop:
            print "Would branch: {}".format(branch)
        else:
            print "Branching '{}'".format(branch)
            branch_and_move(branch)

if __name__ == "__main__":
    main()
