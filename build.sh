#!/bin/bash
# get the version descriptors
ROOT=$( cd "$( dirname "$0")"; pwd)
BRANCH=`git branch | grep "*" | sed 's/\* \(.*\)$/\1/g'`
VERSION=`git describe --tags HEAD`
if [ $? != 0 ]
then
	VERSION=`git describe --always`
fi

# mv that shit to a toplevel dir
mkdir -p "build/dummy"
cp -r src/dummy src/setup.py LICENSE readme.md build/dummy/

# tar that shit
tar -cvzf "dummy-$BRANCH-$VERSION.tgz" -C build dummy bin

# rm the build
rm -r build
