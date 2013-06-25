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
		# format the results using the selected formatter
		return formatter().format_results( self.results, *metrics )

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
	# check if any formatting options were given
	# do this first as it can be verified quickly
	if args.plot:
		from dummy.viewer.formatting import PlotFormatter
		formatter = PlotFormatter
	elif hasattr( args, 'format' ) and args.format is not None:
		# try to find a formatter with that name
		from dummy.viewer.formatting import Formatter
		formatter = Formatter.get( args.format )
	else:
		from dummy.viewer.formatting import LogFormatter
		formatter = LogFormatter

	manager = _parse_results( args )

	# format them in some way
	manager.format( metrics=args.metric, formatter=formatter )

def stat( args ):
	stats = {}
	stat_names = args.stat
	# If no statistics given, load all configured statistics.
	if len( stat_names ) == 0:
		logger.info( "No statistics given, using all configured statistics" )
		stat_names = config.STATISTICS.keys()

	logger.info( "Loading statistics: %s" % stat_names )
	for name in stat_names:
		logger.debug( "Loading statistic `%s`" % name )
		stat = config.STATISTICS.get( name )

		assert stat is not None, "Statistic `%s` is not configured" % name

		# parse the config
		stats[ name ] = Statistic.parse( name, stat )

	# do this after the stats have been parsed
	# as it might take quite a while
	# and the parameters must thus be validated before results are loaded
	manager = _parse_results( args )
	assert len( manager.results ) > 0, \
		"No results to calculate statistics for (have you specified a test?)"

	# compute the statistic
	values = {}
	for name, s in stats.items():
		values[ name ] = s.gather( manager.results )

	# format the stats
	formatter = LogFormatter()
	formatter.format( values )
