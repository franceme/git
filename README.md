# Git Helper

## What is this?

This is a Python3 script to help automate working Git.

> This is not a replacement for git.

You can think of this as an easy "abstraction" or orchestration over Git.

## Why did I make this?

While I was running through multiple git repos, I found it annoying to go back and forth in directories.
I even created multiple bash aliases to just commit and push each repo, but soon discovered various features were missing.
Since Python3 is a great scripting language, I decided to learn more about sub-processes while making my mgmt of Git easier.

## Who can use it?

Anyone who uses a Linux based subsystem (maybe WSL too?) with Python3 should be able to use it.
The libraries should be all Python3 std.

## Why should you use this?

You should use this if you would like a scripting language to easily look throughout Git directories and handle various simpler operations.
This is not perfect so feel free to contribute or change it.

## How do I use it?

This was designed to be used on the cmdline from linux.

> ```./make.py <argument> (<Repo>)```

ex help:
> ```./make.py -h```

## What operations are supported?

> view [<Directory>]
>> Views a single or all of the Git repos in cloned from the .git.json file.
>>
>> ex: ```./make.py view [<franceme/git>]```

> + or clone <Repo>
>> Clones a repo using GitHub client, if the username is not supplied the username from make.py will be used.
>>
>> Once the repo is cloned the repo is written to the .git.json file for tracking.
>>
>> ex: ```./make.py clone [<franceme/git>] #clones git@github.com/franceme/git```
>>
>> ex: ```./make.py clone [<franceme/git>] #clones git@github.com/<gitUserName from make.py>/git```

> - or remove <Repo>
>> Removes the Git repo.
>>
>> Once the repo is removed it is also removed from the .git.json file for tracking.
>>
>> ex: ```./make.py remove [<franceme/git>]```

> ? or status <Repo>
>> Checks the status of the repo specified or all of them
>>
>> ex: ```./make.py status [<franceme/git>]```

> pull [<Directory>]
>> Pulls the repo supplied or all of the repos.
>>
>> ex: ```./make.py pull [<franceme/git>] #pull git@github.com/franceme/git```

> push [<Directory>]
>> Pushes the repo supplied or all of the repos.
>>
>> ex: ```./make.py pull [<franceme/git>] #push git@github.com/franceme/git```

> remote <Directory>
>> Views the branch of the specified repo
>>
>> ex: ```./make.py remote <franceme/git> master```

> sync [<Directory>]
>> Syncs the specified or all of the repos listed
>>
>> This command solely runs the pull and push commands
>>
>> ex: ```./make.py sync [<franceme/git>]```

> branchs [<Directory>]
>> Views the branch of the specified or all of the repos listed
>>
>> ex: ```./make.py branchs [<franceme/git>]```

> branch [<Directory>]
>> Changes the  the branchs of the specified repos
>>
>> ex: ```./make.py <franceme/git> <repo branch>```

> remote <Directory>
>> Views the branch of the specified repo
>>
>> ex: ```./make.py remote <franceme/git> master```

> bfg
>> Lists the following commands to use bfg, truly not helpful but a good reminding.
>>
>> ex: ```./make.py bfg.```
