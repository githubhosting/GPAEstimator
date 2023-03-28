#!/bin/bash -x
# extract the list of submodules from .gitmodule
cat .gitmodules |while read i
do
if [[ $i == \[submodule* ]]; then
    echo converting $i

    # extract the module's prefix
    mpath=$(echo $i | cut -d\" -f2)

    # skip two lines
    read i; read i;

    # extract the url of the submodule
    murl=$(echo $i|cut -d\= -f2|xargs)

    # extract the module name
    mname=$(basename $mpath)

    # deinit the module
    git submodule deinit $mpath

    # remove the module from git
    git rm -r --cached $mpath

    # remove the module from the filesystem
    rm -rf $mpath

    # commit the change
    git commit -m "Removed $mpath submodule"

    # add the remote
    git remote add -f $mname $murl

    # add the subtree
    git subtree add --prefix $mpath $mname master --squash

    # fetch the files
    git fetch $murl master
fi
done
git rm .gitmodules
