'''
Created on May 17, 2014

@author: ignacio
'''
import subprocess

def get_git_root():
    command = ['rev-parse', '--show-toplevel']
    proc = _run_command(command)
    return proc.stdout.readline().strip()

def _run_command(command):
    command = ["git"] + command
    proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    proc.wait()

    if proc.poll():
        raise ValueError("Command {} failed. Is this a git repo?".format(command))
    return proc
