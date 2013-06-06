#!/bin/bash
# get the version descriptors
ROOT=$( cd "$( dirname "$0")"; pwd)
BRANCH=`git branch | grep "*" | sed 's/\* \(.*\)$/\1/g'`
VERSION=`git describe --tags HEAD`
if [ $? != 0 ]
then
	VERSION=`git describe --always`
fi

# creating the dist dir
rm -rf dist/
mkdir dist/
cp -rf src dist/dummy

# tar that shit
tar -cvzf "dummy-$BRANCH-$VERSION.tgz" -C dist dummy
