#!/bin/bash

ROOT="$( cd "$0/../.."; pwd )"
PYTHONPATH="$ROOT/src/:$PYTHONPATH"

if [ "$1" == '' ]
then
	echo "Test script run without argument";
	exit 1;
fi

cd $1

python -m unittest discover
