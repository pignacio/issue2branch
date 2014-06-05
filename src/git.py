'''
Created on May 17, 2014

@author: ignacio
'''
import subprocess
import re
import os

BRANCH_NAME_RE = r"[a-zA-Z0-9#]+"


def get_git_root():
    repo_dir = os.getcwd()
    while not os.path.isdir(os.path.join(repo_dir, ".git")):
        repo_dir, child = os.path.split(repo_dir)
        if not child:
            raise ValueError("'{}' is not inside a git repository"
                             .format(os.getcwd()))
    return repo_dir


def get_remotes():
    command = ['remote', '--verbose']
    proc = _run_command(command)
    remotes = {}
    for line in proc.stdout:
        name, url = line.split()[:2]
        remotes[name] = url
    return remotes


def branch_and_move(branch):
    if _branch_exists(branch):
        _run_command(['checkout', branch])
    else:
        _run_command(['checkout', '-b', branch])


def _branch_exists(branch):
    try:
        _run_command(["show-ref", "--verify", "--quiet",
                      "refs/heads/{}".format(branch)])
        return True
    except ValueError:
        return False


def _run_command(command):
    command = ["git"] + command
    proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    proc.wait()

    if proc.poll():
        raise ValueError("Command {} failed. Is this a git repo?"
                         .format(command))
    return proc


def get_branch_name(title):
    return "-".join(re.findall(BRANCH_NAME_RE, title)).lower()
