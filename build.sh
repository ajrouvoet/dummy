#!/bin/bash
# get the version descriptors
ROOT=$( cd "$( dirname "$0")"; pwd)
BRANCH=`git branch | grep "*" | sed 's/\* \(.*\)$/\1/g'`
VERSION=`git describe --tags HEAD`
if [ $? != 0 ]
then
	VERSION=`git describe --always`
fi

# tar that shit
tar -cvzf "dummy-$BRANCH-$VERSION.tgz" LICENSE README -C src dummy bin setup.py
