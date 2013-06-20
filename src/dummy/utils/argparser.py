import logging

from dummy.models import Test
from dummy.utils import git
from dummy.storage import StorageProvider
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

	# expand excludes using globbing
	excludes = []
	for ex in args.exclude:
		excludes += Test.glob( ex )

	# unqueue excluded tests
	tests = [ t for t in tests if t.name not in excludes ]

	# unqueue tests that already have results
	# if complement option is given
	if args.complement:
		targets = discover_targets( args )
		commit = args.commit or git.describe()

		# assume tested
		filtered = []
		for test in tests:
			tested = True
			for t in targets:
				if not StorageProvider.exists( commit, t, test ):
					tested = False

			if not tested:
				filtered.append( test )

		tests = filtered

	return tests
