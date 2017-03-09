#!/bin/bash

# tail n+2 will start the file from the second line
# <() is called process substitution in this case will add a new line between
# the files
git log -1 | tail -n+2 > tmp && cat tmp <(echo) ChangeLog > ChangeLog_tmp

rm tmp && mv ChangeLog ChangeLog_bkp && mv ChangeLog_tmp ChangeLog

git add ChangeLog

# The -C option will use the previous commit message without asking to change it
# and also the timestamp
git commit -C HEAD --amend
