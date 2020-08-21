#!/usr/bin/env python3
'''
@author franceme

'''

import hashlib
import json
import os
import shlex
import signal
import subprocess
import sys
import fileinput
import time
import pwd
from glob import glob as re

'''####################################
#A utility class that contains the rest of the main common files
'''  ####################################

gitUserName = 'franceme'

# region Properties Loader
class Reader():
    def __init__(self, name = '.git.json'):
        self.fileName = name
        self.data = None

    def __enter__(self):
        if not os.path.exists(self.fileName):
            with open(self.fileName,'w') as foil:
                foil.write('{}')
        with open(self.fileName, 'r') as foil:
            self.data = json.load(foil)
        return self

    def __exit__(self, type, value, traceback):
        os.system('mv ' + str(self.fileName) + ' ' + str(self.fileName)+'.bak')
        with open(self.fileName, 'w') as foil:
            json.dump(self.data,foil,indent=4)

    def __iadd__(self, obj, vcs='git clone git@github.com:'):
        Utils.run(f"{vcs}{obj}")
        self.data[obj] = {"Stashed":[]}
        return self.data

    def __isub__(self, name):
        reponame = None
        for repo in self.data:
            if name.replace('/','') == Utils.path(repo):
                reponame = repo
                Utils.run(f"rm -r {name}")
        self.data.pop(reponame)
        return self.data
# endregion
# region Hooks
class Hooks(object):
    def cloneHook(repo):
        with Reader() as info:
            _repo, _reponame = None, None
            for fullrepo in info.data.keys():
                if Utils.path(fullrepo) + '/' == repo:
                    _repo, _reponame = info.data[fullrepo], fullrepo
            if _reponame in repos.keys():
                base_path = Utils.path(repo) + '/'
                if 'findreplace' in repos[fullrepo]:
                    for sect in repos[fullrepo]['findreplace']:
                        foil = base_path + sect['file']
                        with fileinput.FileInput(foil, inplace=True) as file:
                            for line in file:
                                print(line.replace(sect['find'], sect['replace']), end='')
                if 'exclude' in repos[fullrepo]:
                    for globbing in repos[fullrepo]['exclude']:
                        starter, ender, glober, capture = globbing['regionStart'], globbing['regionEnd'], globbing['glob'], False
                        for foil in re(glober):
                            with fileinput.FileInput(foil, inplace=True) as file:
                                for line in file:
                                    if line.strip().startswith(starter):
                                        print(line.replace('\n',''))
                                        if len(_repo['Stashed']) > 0:
                                            [print(line.replace('\n','')) for line in _repo['Stashed'].pop(0).split('\n')]
                                    else:
                                        print(line.replace('\n',''))

    def cmtHook(repo):
        with Reader() as info:
            _repo, _reponame = None, None
            for fullrepo in info.data.keys():
                if Utils.path(fullrepo) + '/' == repo:
                    _repo, _reponame = info.data[fullrepo], fullrepo
            if fullrepo in repos.keys():
                print("Caught Here")
                base_path = Utils.path(repo) + '/'
                if 'findreplace' in repos[fullrepo]:
                    for sect in repos[fullrepo]['findreplace']:
                        foil = base_path + sect['file']
                        with fileinput.FileInput(foil, inplace=True) as file:
                            for line in file:
                                print(line.replace(sect['replace'], sect['find']), end='')
                if 'exclude' in repos[fullrepo]:
                    for globbing in repos[fullrepo]['exclude']:
                        starter, ender, glober, capture = globbing['regionStart'], globbing['regionEnd'], globbing['glob'], False
                        temp_lines = []
                        for foil in re(glober):
                            with fileinput.FileInput(foil, inplace=True) as file:
                                for line in file:
                                    if capture and not line.strip().startswith(ender):
                                        if line != '':
                                            temp_lines += [line.replace('\n','')]
                                    elif line.strip().startswith(starter):
                                        capture = True
                                        print(line.replace('\n',''))
                                    elif line.strip().startswith(ender):
                                        capture = False
                                        print(line.replace('\n',''))
                                        _repo['Stashed'] += ['\n'.join(temp_lines)]
                                        temp_lines = []
                                    else:
                                        print(line.replace('\n',''))
# endregion
# region Cmds
class Cmds(object):
    def sha(foil, debug=True):
        if debug:
            print(f"Determining the sha512 sum of file {foil}")
        sha = None
        with open(foil, 'rb') as new:
            contents = new.read()
            sha = hashlib.sha512(contents).hexdigest()
        return sha

    def view(argz):
        print('Viewing Repos')
        print('===============================')
        with Reader() as info:
            for value in info.data:
                print(value)
        print('===============================')

    def bfg(argz):
        print("""
        git clone --mirror git@github.com:<repo>.git
        bfg -rt ~/.sdkman/candidates/bfg/lists/<repo>.txt --no-blob-protection <repo>.git/
        cd <repo>.git
        git reflog expire --expire=now --all && git gc --prune=now --aggressive
        git push -f
        rm -r <repo>.git
        """)

    def clone(argz):
        with Reader() as info:
            for repo in argz:
                print('Cloning the repo: ' + str(repo))

                if '/' not in repo:
                    global gitUserName
                    repo = f"{gitUserName}/{repo}"

                info += repo
                Hooks.cloneHook(repo)

    def push(argz):
        if argz is None or len(argz)==0:
            with Reader() as info:
                for repo in info.data:
                    Hooks.cmtHook(repo)
                    print(f"Pushing the Repo {repo}")
                    cmdz = [
                        f"git -C {Utils.path(repo)} add .",
                        f"git -C {Utils.path(repo)} rm .",
                        f"git -C {Utils.path(repo)} commit -m \"Update\" -S",
                        f"git -C {Utils.path(repo)} push",
                    ]
                    [Utils.run(cmd) for cmd in cmdz]
                    Hooks.cloneHook(repo)
                print('===============================')
        else:
            for repo in argz:
                Hooks.cmtHook(repo)
                print(f"Pushing the Repo {repo}")
                cmdz = [
                    f"git -C {repo} add .",
                    f"git -C {repo} rm .",
                    f"git -C {repo} commit -m \"Update\" -S",
                    f"git -C {repo} push",
                ]
                [Utils.run(cmd) for cmd in cmdz]
                Hooks.cloneHook(repo)

    def branch(argz):
        if argz is None or len(argz)==0:
            print('Please specify a repo')
            sys.exit(-1)
        elif len(argz)==1:
            print('Please specify a branch')
            sys.exit(-1)
        elif len(argz) > 2:
            print('There are too many arguments')
            sys.exit(-1)
        else:
            cmd = f"git -C {argz[0]} checkout {argz[1]}"
            Utils.run(cmd)

    def branchs(argz):
        if argz is None or len(argz)==0:
            print('Please specify a repo')
            sys.exit(-1)
        else:
            cmd = f"git -C {argz[0]} branch"
            Utils.run(cmd)

    def verify(argz):
        old, new = [], Cmds.walk(False)
        with open('hash.sums','r') as foil:
            for line in foil.readlines():
                old += [line]
        print(list(set(old) - set(new)))

    def create(argz):
        with open('hash.sums', 'w') as foil:
            for line in Cmds.walk():
                foil.write(f"{line}\n")

    def walk(debug = True):
        filez = []
        for (dirpath,dirname, filenames) in os.walk('./'):
            for filename in filenames:
                if filename not in ['hash.sums','.git.json.bak','.git.json','.log','make.py']:
                    file = dirpath+'/'+filename
                    sha = Cmds.sha(file,debug)
                    filez += [f"{sha}  {file}"]
        return filez

    def sync(argz):
        Cmds.update(argz)
        Cmds.push(argz)
    
    def issues(argz):
        Cmds.gh_simple(argz, 'issue list','Viewing the issues of')

    def status(argz):
        Cmds.simple(argz, 'status','Checking the status of')

    def remote(argz):
        Cmds.simple(argz, 'remote -v','Checking the Remote of')

    def update(argz):
        Cmds.simple(argz, 'pull','Pulling the status of')
    
    def gh_simple(argz, cmd, exp):
        if argz is None or len(argz)==0:
            with Reader() as info:
                for repo in info.data:
                    Hooks.cmtHook(repo)
                    print(f"{exp} the Repo {repo}")
                    runner = f"gh {cmd}"
                    Utils.run(runner, Utils.path(repo))
                    print('\n')
                    Hooks.cloneHook(repo)
                print('===============================')
        else:
            for repo in argz:
                Hooks.cmtHook(repo)
                print(f"{exp} the Repo {repo}")
                runner = f"gh {cmd}"
                Utils.run(runner, repo)
                Hooks.cloneHook(repo)

    def simple(argz, cmd, exp):
        if argz is None or len(argz)==0:
            with Reader() as info:
                for repo in info.data:
                    Hooks.cmtHook(repo)
                    print(f"{exp} the Repo {repo}")
                    runner = f"git -C {Utils.path(repo)} {cmd}"
                    Utils.run(runner)
                    print('\n')
                    Hooks.cloneHook(repo)
                print('===============================')
        else:
            for repo in argz:
                Hooks.cmtHook(repo)
                print(f"{exp} the Repo {repo}")
                runner = f"git -C {repo} {cmd}"
                Utils.run(runner)
                Hooks.cloneHook(repo)

    def remove(argz):
        with Reader() as info:
            for repo in argz:
                info -= repo
# endregion
# region Utils
class Utils(object):
    def path(repo):
        return repo.split('/')[1]
    def get(repoName):
        with Reader() as info:
            for repo in info.data.keys():
                if Utils.path(repo) == repoName:
                    return repo
            return None
    def run(command, subdir=None):
        os.setuid(pwd.getpwuid(os.getuid()).pw_uid)
        print(f"Running the command: {command}")
        if subdir is not None:
            os.chdir(subdir)
        temp=subprocess.Popen(('yes'),stdout=subprocess.PIPE)
        process = subprocess.Popen(shlex.split(command),stdin=temp.stdout, stdout=subprocess.PIPE)
        while True:
            output = process.stdout.readline()
            if output == '' or process.poll() is not None:
                break
            if output:
                outputString = '\t' + str(output.strip())[2:-1].replace('\\t','\t')
                print(outputString)
        if subdir is not None:
            os.chdir('../')

    def start():
        if len(sys.argv) == 1:
            cmd, argz = 'view', []
        else:
            cmd, argz = sys.argv[1], sys.argv[2:]
        routers[cmd]["func"](argz)
# endregion
# region Hooks
repos = {
    'example': {
        'findreplace': [
            {
                'file':'FILEHERE',
                'find':'RAWPASSWORD',
                'replace':"PASSWORDHERE"
            }
        ],
        "exclude": {
            "regionStart":"//excludeRegionStart",
            "regionEnd":"//excludeRegionEnd"

        }
    },
}
# endregion
# region Routers
'''####################################
#The dictionary containing the working functions and their respective definitions
'''  ####################################
routers = {
    'view': {
        "func": Cmds.view,
        "def": "Views all of the repos listed"
    },
    '+': {
        "func": Cmds.clone,
        "def": "Clones the repo listed"
    },
    'clone': {
        "func": Cmds.clone,
        "def": "Clones the repo listed"
    },
    'pull': {
        "func": Cmds.update,
        "def": "Updates the repo listed or all of them"
    },
    'push': {
        "func": Cmds.push,
        "def": "Pushes the repo listed or all of them"
    },
    'remote': {
        "func": Cmds.remote,
        "def": "Views the remove for the repo listed or all of them"
    },
    '-': {
        "func": Cmds.remove,
        "def": "Removes the repo listed"
    },
    'remove': {
        "func": Cmds.remove,
        "def": "Removes the repo listed"
    },
    'sync': {
        "func": Cmds.sync,
        "def": "Syncs the repo listed"
    },
    '?': {
        "func": Cmds.status,
        "def": "Checks the status of the repo listed"
    },
    'status': {
        "func": Cmds.status,
        "def": "Checks the status of the repo listed"
    },
    'branch': {
        "func": Cmds.branch,
        "def": "Changes the branch of the specified repo"
    },
    'branchs': {
        "func": Cmds.branchs,
        "def": "Views the branchs of the specified repo"
    },
    'bfg': {
        "func": Cmds.bfg,
        "def": "Shows the commands to use BFG"
    },
    'issues': {
        "func": Cmds.issues,
        "def": "Shows the issues of the repo listed"
    },
}


# endregion

def signal_handler(sig, frame):
    print('\nExiting...')
    sys.exit(0)

'''####################################
#The main runner of this file, intended to be ran from
'''  ####################################
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    if len(sys.argv) == 2 and (sys.argv[1] not in routers.keys()):
        print('Please Enter a valid argument')
        print('=============================')
        [print('\t./make.py ' + str(arg) + ": " + str(routers[arg]['def'])) for arg in routers.keys()]
    else:
        Utils.start()
