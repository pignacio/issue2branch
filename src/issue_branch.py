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
    parser.add_argument("-t", "--take",
                        action='store_true', default=False,
                        help="Sets yourself as the assignee, if possible")
    return parser


def _parse_args():
    parser = _get_arg_parser()
    options = parser.parse_args()
    if not options.list and options.issue is None:
        raise ValueError("Must supply --list or a issue")
    return options


def main():
    options = _parse_args()

    def _op(message, callback, *args, **kwargs):
        if options.noop:
            print "(noop) {}".format(message)
        else:
            print message
            callback(*args, **kwargs)

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
        _list_issues(issues)
    else:
        print "Getting issue title for issue: '{}'".format(options.issue)
        title = tracker.get_issue_title(options.issue)
        print "Got title: '{}'".format(title)
        branch = "-".join(re.findall(BRANCH_NAME_RE, title)).lower()
        _op("Branching '{}'".format(branch),
            branch_and_move, branch)

        if options.take:
            try:
                _op("Taking issue: {}".format(options.issue),
                    tracker.take_issue, options.issue)
            except NotImplementedError:
                print ("[ERROR] Issue taking is not implemented for {}"
                       .format(tracker.__class__))


def _list_issues(issues, indent=0):
    for issue_id, issue_data in sorted(issues.items()):
        try:
            text = issue_data['text']
            childs = issue_data.get('childs', {})
        except (KeyError, TypeError):
            text = issue_data
            childs = {}
        print "{} * {} - {}".format("  " * indent, issue_id, text)
        _list_issues(childs, indent=indent + 1)


if __name__ == "__main__":
    main()
