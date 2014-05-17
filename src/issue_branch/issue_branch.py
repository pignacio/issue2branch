#!/usr/bin/env python
import os
import re
import sys

from config import get_config
from trackers import get_issue_tracker


BRANCH_NAME_RE = r"[a-zA-Z0-9\s\-_]"


def main():
    if len(sys.argv) < 2:
        raise ValueError("No issue supplied")
    issue = sys.argv[1]
    config = get_config()
    tracker = get_issue_tracker(config)

    title = tracker.get_issue_title(issue)
    print "Got title: '{}'".format(title)
    branch = re.sub("\s+", "-", "".join(re.findall(BRANCH_NAME_RE, title)).lower())

    print "Branching '{}'".format(branch)

    os.system("git checkout -b {}".format(branch))

if __name__ == "__main__":
    main()
