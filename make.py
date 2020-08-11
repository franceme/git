#!/usr/bin/env python3

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

'''####################################
#A utility class that contains the rest of the main common files
'''  ####################################

# region Properties Loader
class Reader():
    def __init__(self, name = '.git.json'):
        self.fileName = name
        self.data = None

    def __enter__(self):
        with open(self.fileName, 'r') as foil:
            self.data = json.load(foil)
        return self

    def __exit__(self, type, value, traceback):
        os.system('mv ' + str(self.fileName) + ' ' + str(self.fileName)+'.bak')
        with open(self.fileName, 'w') as foil:
            json.dump(self.data,foil,indent=4)

    def __iadd__(self, obj, vcs='git clone git@github.com:'):
        Utils.run(f"{vcs}{obj}")
        self.data += [obj]
        return self.data

    def __isub__(self, name):
        for repo in self.data:
            if name == Utils.path(repo):
                self.data.remove(repo)
                Utils.run(f"rm -r {name}")
        return self.data
# endregion
# region Cmds
class Cmds(object):
    def sha(foil, debug=True):
        if debug:
            print(f"Determining the sha256 sum of file {foil}")
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
                    repo = 'franceme/'+repo

                info += repo
                Cmds.cloneHook(repo)

    def cloneHook(repo):
        if repo in repos.keys():
            base_path = Utils.path(repo) + '/'
            for sect in repos[repo]['findreplace']:
                foil = base_path + sect['file']
                with fileinput.FileInput(foil, inplace=True) as file:
                    for line in file:
                        print(line.replace(sect['find'], sect['replace']), end='')

    def cmtHook(repo):
        if repo in repos.keys():
            base_path = Utils.path(repo) + '/'
            for sect in repos[repo]['findreplace']:
                foil = base_path + sect['file']
                with fileinput.FileInput(foil, inplace=True) as file:
                    for line in file:
                        print(line.replace(sect['replace'], sect['find']), end='')

    def push(argz):
        if argz is None or len(argz)==0:
            with Reader() as info:
                for repo in info.data:
                    Cmds.cmtHook(repo)
                    print(f"Pushing the Repo {repo}")
                    cmdz = [
                        f"git -C {Utils.path(repo)} add .",
                        f"git -C {Utils.path(repo)} rm .",
                        f"git -C {Utils.path(repo)} commit -m \"Update\" -S",
                        f"git -C {Utils.path(repo)} push",
                    ]
                    [Utils.run(cmd) for cmd in cmdz]
                    Cmds.cloneHook(repo)
                print('===============================')
        else:
            for repo in argz:
                Cmds.cmtHook(repo)
                print(f"Pushing the Repo {repo}")
                cmdz = [
                    f"git -C {repo} add .",
                    f"git -C {repo} rm .",
                    f"git -C {repo} commit -m \"Update\" -S",
                    f"git -C {repo} push",
                ]
                [Utils.run(cmd) for cmd in cmdz]
                Cmds.cloneHook(repo)

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

    def status(argz):
        Cmds.simple(argz, 'status','Checking the status of')

    def remote(argz):
        Cmds.simple(argz, 'remote -v','Checking the Remote of')

    def update(argz):
        Cmds.simple(argz, 'pull','Pulling the status of')

    def simple(argz, cmd, exp):
        if argz is None or len(argz)==0:
            with Reader() as info:
                for repo in info.data:
                    Cmds.cmtHook(repo)
                    print(f"{exp} the Repo {repo}")
                    runner = f"git -C {Utils.path(repo)} {cmd}"
                    Utils.run(runner)
                    print('\n')
                    Cmds.cloneHook(repo)
                print('===============================')
        else:
            for repo in argz:
                Cmds.cmtHook(repo)
                print(f"{exp} the Repo {repo}")
                runner = f"git -C {repo} {cmd}"
                Utils.run(runner)
                Cmds.cloneHook(repo)

    def remove(argz):
        with Reader() as info:
            for repo in argz:
                info -= repo



# endregion
# region Utils
class Utils(object):
    def path(repo):
        return repo.split('/')[1]
    def run(command):
        os.setuid(pwd.getpwuid(os.getuid()).pw_uid)
        print(f"Running the command: {command}")
        process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
        while True:
            output = process.stdout.readline()
            if output == '' or process.poll() is not None:
                break
            if output:
                print(output.strip())

    def start():
        if len(sys.argv) == 1:
            cmd, argz = 'view', []
        else:
            cmd, argz = sys.argv[1], sys.argv[2:]
        routers[cmd]["func"](argz)
# endregion
# region Hooks
repos = {
    'franceme/Cryptoguard': {
        'findreplace': [
            {
                'file':'build.gradle',
                'find':'JAVA7SDK',
                'replace':"JAVA7SDK"
            },
            {
                'file':'build.gradle',
                'find':'JAVA8SDK',
                'replace':"JAVA8SDK"
            },
            {
                'file':'build.gradle',
                'find':'ANDROIDSDK',
                'replace':"ANDROIDSDK"
            }
        ]
    },
    'franceme/cryptoguard': {
        'findreplace': [
            {
                'file':'build.gradle',
                'find':'JAVA7SDK',
                'replace':"JAVA7SDK"
            },
            {
                'file':'build.gradle',
                'find':'JAVA8SDK',
                'replace':"JAVA8SDK"
            },
            {
                'file':'build.gradle',
                'find':'ANDROIDSDK',
                'replace':"ANDROIDSDK"
            }
        ]
    }
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
    #'create': {
    #    "func": Cmds.create,
    #    "def": "Creates a sha of all the files"
    #},
    #'verify': {
    #    "func": Cmds.verify,
    #    "def": "Compares the sha of all of the files"
    #},
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
