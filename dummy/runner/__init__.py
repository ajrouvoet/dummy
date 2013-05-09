from dummy import config
from dummy.models import Test

import os
import glob
import subprocess

# subprogram run
def run( args ):
	name = args.name
	queue = []

	# check if we need to run a whole test suite
	if args.suite:
		# make sure to have a valid test suite name
		suite = config.SUITES.get( name )
		assert suite is not None,\
			"We looked, but a test suite with name `%s` was not found." % name

		for name in suite:
			for fname in Test.glob( name ):
				queue.append( Test( fname ))

	# if not running a whole suite
	# just queue the one named test
	else:
		queue.append( Test( name ))

	# run the tests in the queue
	for t in queue:
		print( "Running %s" % t.name )
		t.run()
