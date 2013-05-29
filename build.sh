#!/bin/bash
HASH=`git describe --always`

if [ "$1" = "-f" ]
then
	tar -cvzf "dummy.$HASH.tar.gz" dummy/ -C python/lib/python2.7/ site-packages/
else
	tar -cvzf "dummy.$HASH.tar.gz" dummy/
fi
