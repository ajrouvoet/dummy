from dummy import config

import os
import subprocess

# subprogram run
def run( args ):
	# assemble the path to the test/suite
	# and make sure it exists
	path = os.path.join( config.TESTS_DIR, args.name )
	assert os.path.exists( path ), "Sorry, could not find the test `%s`" % args.name

	subprocess.call([ config.TEST_RUNNER, path ])
