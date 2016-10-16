from __future__ import absolute_import, unicode_literals, division

import os
import logging

from .config import get_config
from .trackers import get_issue_tracker


def main():
    debug = os.environ.get('ISSUE2BRANCH_DEBUG', False)
    if debug:
        level = str(debug).upper()
        if level not in ['INFO', 'DEBUG', 'WARNING', 'WARN', 'CRITICAL']:
            level = 'INFO'
        logging.basicConfig(level=level)
    config = get_config()
    get_issue_tracker(config).run(config)


if __name__ == "__main__":
    main()
