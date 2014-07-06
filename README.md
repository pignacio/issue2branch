issue-branch
============

Feature branch namer

Installation
-----------

At the time of this writing, `GitPython` fails to install correctly, as only
beta and RC version are listed in PyPI after 0.3.0, and, for example,
`GitPython==0.3.1-beta2` installs as `0.3.1`.

The easiest way I found to get away from this is installing `GitPython` by hand
before `issue-branch`, and ensure a version `>=0.3.1`.

```
pip install GitPython==0.3.1-beta2
pip install issue-branch
```
