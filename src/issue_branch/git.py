'''
Created on May 17, 2014

@author: ignacio
'''
import subprocess

def get_git_root():
    command = ['git', 'rev-parse', '--show-toplevel']
    proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    proc.wait()

    if proc.poll():
        raise ValueError("Could not get git root directory. Is this a git repo?")
    return proc.stdout.readline().strip()
