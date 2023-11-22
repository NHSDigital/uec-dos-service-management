#!/bin/bash

rm -f .git/hooks/pre-commit
cp scripts/git/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

rm -f .git/hooks/commit-msg
cp scripts/git/commit-msg .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg

git config branch.autosetupmerge false    
git config branch.autosetuprebase always    
git config commit.gpgsign true    
git config core.autocrlf input    
git config core.filemode false    
git config core.hidedotfiles false    
git config core.ignorecase false    
git config pull.rebase true    
git config push.default current    
git config push.followTags true    
git config rebase.autoStash true    
git config remote.origin.prune true git
