#!/bin/bash
HASH=`git describe --always`
tar -cvzf "dummy.$HASH.tar.gz" dummy/ -C python/lib/python2.7/ site-packages/
