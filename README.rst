issue2branch
============

.. image:: https://pypip.in/version/issue2branch/badge.svg?style=flat
    :target: https://pypi.python.org/pypi/issue2branch/
    :alt: Latest version

.. image:: https://pypip.in/py_versions/issue2branch/badge.svg?style=flat
    :target: https://pypi.python.org/pypi/issue2branch/
    :alt: Supported Python versions

.. image:: https://travis-ci.org/pignacio/issue2branch.svg?branch=master
    :target: https://travis-ci.org/pignacio/issue2branch

.. image:: https://coveralls.io/repos/pignacio/issue2branch/badge.svg?branch=master
    :target: https://coveralls.io/r/pignacio/issue2branch?branch=master


.. image:: https://pypip.in/license/issue2branch/badge.svg?style=flat
    :target: https://pypi.python.org/pypi/issue2branch/
    :alt: License


A helper for naming feature branches with git

This app fetches issue titles from different issue trackers, and checkouts
feature branches with nice names ::

    pignacio/issue2branch ‹master› % issue2branch 4
    Getting issue title for issue: '4'
    Requesting 'https://api.github.com/repos/pignacio/issue2branch/issues/4'
    Got title: 'Issue 4 Write README'
    Branching 'issue-4-write-readme'
    pignacio/issue2branch ‹issue-4-write-readme› %

Installation
------------

::

    pip install issue2branch


Usage
-----

::

    issue2branch --list          # -l/--list: show the current open issues
    issue2branch -l --limit 50   # --limit the amount of issues listed
    issue2branch -s <issue>      # -s/--show: print the issue description
    issue2branch <issue>         # Fetch the <issue> title and checkout a branch
    issue2branch <issue> --take  # Additionally, set yourself as the assignee, when
                                 # possible
    issue2branch <issue> --noop  # -n/--noop runs dry (without making changes)


Additional redmine usages
*************************

Redmine supports additional parameters::

    issue2branch --list --mine       # -m/--mine show only tickes assigned to you
    issue2branch --list -v <version> # -v/--version filter by target version
    issue2branch --list --all        # List all (including closed) issues
    issue2branch --project myproject # -p/--project filter issues by project
    issue2branch --all-projects      # Show all projects

Supported issue trackers
------------------------

* `Github  <http://www.github.com)>`_ and `Bitbucket <http://www.bitbucket.org>`_
  public issue trackers are supported out of the box. For private ones, auth
  tokens must be added.
* `Redmine  <http://www.redmine.org>`_

Configuration
-------------

The configuration file default location is `<git repo
root>/.issue2branch.config`, and can be overriden via the `ISSUE2BRANCH_CONFIG`
enviroment variable.

The file follows the `ConfigParser` format and has the following sections::


    [main]
    tracker = issue tracker type. one of redmine, github, bitbucket.
              Github and Bitbucket are detected automatically based on the origin
              remote hostname

    [auth]
    user = HTTP authentication user
    password = HTTP authentication password, if missing when user is present, a
               prompt will ask for it each time issue2branch is run

    [list]  # --list options
    limit = number of issues to retrieve when listing. Defaults to 40.
            Is overrided at runtime via the --limit argument

    [redmine] # Redmine specific config
    url = url where the issue tracker is located
    inprogress_id = Internal redmine ID for the "In progress" status. Needed for
                    --take
    assignee_id = Internal redmine ID for the assignee. Needed for --take
    project = Only show issues from this project

    [github] # Github specific config
    repo_user = the owner of the issue tracker. Useful for overriding real owner
                when working on a fork. Defaults to origin's owner
    repo_name = name of the remote repo. Defaults to origins's name

    [bitbucket] # Bitbucket specific config
    repo_user = the owner of the issue tracker. Useful for overriding real owner
                when working on a fork. Defaults to origin's owner
    repo_name = name of the remote repo. Defaults to origins's name
