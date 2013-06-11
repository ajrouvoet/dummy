import logging

from dummy import config
from dummy.utils import git, argparser
from dummy.storage import JsonStorageProvider
from dummy.viewer.formatting import LogFormatter
from dummy.statistics import Statistic

logger = logging.getLogger( __name__ )

class ResultManager:
	""" Manages test results and can output them with the specified method.
	"""
	def __init__( self ):
		self.results = []

	def load_results( self, commit=git.describe(), targets=[ config.DEFAULT_TARGET ], tests=[] ):
		""" Load results based on the passed commit, targets and tests
		"""
		for target in targets:
			config.set_target( target )
			for test in tests:
				try:
					self.add_result( JsonStorageProvider.load( commit, target, test ))
				except ValueError as e:
					logger.error( "No test results exists yet for test `%s`" % test.name )
					raise

	def add_result( self, result ):
		""" Add a TestResult to this ResultManager.
		"""
		self.results.append( result )

	def format( self, metrics, formatter=LogFormatter ):
		""" Format the results into the specified format.

			.. kwargs:
				.. formatter:
					formatter to use to format the results;
					defaults to 'dummy.viewer.formatting.LogFormatter'

			:return formatter.format return value

			:raises AssertionError: When the method is not supported.
		"""
		# serialise the results
		results = [ s.serialize() for s in self.results ]

		# filter the metrics
		for s in results:
			# Format metrics
			# If no metrics given, format all metrics
			# Note: You cannot do metrics = testresult.metrics, because of th next loop.
			if len( metrics ) == 0:
				dometrics = s.metrics.keys()
			else:
				dometrics = metrics

			s[ 'metrics' ] = {
				key: value
				for ( key, value ) in s[ 'metrics' ].items()
				if key in dometrics
			}

		# format the results using the selected formatter
		concat = []
		f = formatter( title="{name} ({commit})" )
		for s in results:
			concat.append( f.format( s ))

		return concat

def _parse_results( args ):
	# discover the commit
	commit = 'HEAD'
	if args.commit is not None:
		logger.debug( "Loading result from committish `%s`" % args.commit )
		commit = args.commit

	# discover the tests and the targets
	# to load results for
	tests = argparser.discover_tests( args )
	targets = argparser.discover_targets( args )

	# load the test results
	manager = ResultManager()
	manager.load_results( commit=commit, tests=tests, targets=targets )

	return manager

def show( args ):
	manager = _parse_results( args )

	# check if any formatting options were given
	if args.plot:
		from dummy.viewer.formatting import PlotFormatter
		formatter = PlotFormatter
	else:
		from dummy.viewer.formatting import LogFormatter
		formatter = LogFormatter

	# format them in some way
	manager.format( metrics=args.metric, formatter=formatter )

def stat( args ):
	manager = _parse_results( args )
	assert len( manager.results ) > 0, \
		"No results to calculate statistics for (have you specified a test?)"

	logger.info( "Loading statistics..." )

	stats = {}
	for name in args.stat:
		logger.debug( "Loading statistic `%s`" % name )
		stat = config.STATISTICS.get( name )

		assert stat is not None, "Statistic `%s` is not configured" % name

		# parse the config
		s = Statistic.parse( name, stat )

		# compute the statistic
		stats[ name ] = s.gather( manager.results )

	# format the stats
	for name, stat in stats.items():
		formatter = LogFormatter( title=name )
		formatter.format( stat )
