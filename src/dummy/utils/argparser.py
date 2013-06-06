import logging

from dummy.models import Test
from dummy import config

logger = logging.getLogger( __name__ )

def discover_targets( args ):
	targets = []

	if args.alltargets:
		for t in config.TARGETS.keys():
			targets.append( t )
	elif len( args.target ) == 0:
		targets.append( config.DEFAULT_TARGET )
	else:
		for target in args.target:
			targets.append( target )

	return targets

def discover_tests( args ):
	tests = []

	# try to find the suites and append the testnames
	# of the suite
	for name in args.suite:
		logger.info( "Loading tests from suite `%s`" % name )
		# make sure to have a valid test suite name
		try:
			suite = config.SUITES[ name ]
			for descr in suite:
				for fname in Test.glob( descr ):
					logger.debug( "Adding test `%s` to tests." % fname )
					tests.append( Test( fname ))
		except KeyError:
			logger.error( "We looked, but a test suite with name `%s` was not found." % name )

	# queue the named tests
	for names in [ Test.glob( name ) for name in args.tests ]:
		for name in names:
			tests.append( Test( name ))

	return tests
