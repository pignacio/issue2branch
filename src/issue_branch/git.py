'''
Created on May 17, 2014

@author: ignacio
'''
import subprocess

def get_git_root():
    command = ['rev-parse', '--show-toplevel']
    proc = _run_command(command)
    return proc.stdout.readline().strip()

def get_remotes():
    command = ['remote', '--verbose']
    proc = _run_command(command)
    remotes = {}
    for line in proc.stdout:
        name, url = line.split()[:2]
        remotes[name] = url
    return remotes

def _run_command(command):
    command = ["git"] + command
    proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    proc.wait()

    if proc.poll():
        raise ValueError("Command {} failed. Is this a git repo?".format(command))
    return proc
