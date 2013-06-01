import logging

from dummy import config
from dummy.utils import git, argparser
from dummy.storage import JsonStorageProvider
from dummy.viewer.formatters import LogFormatter

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
					defaults to 'dummy.viewer.formatters.LogFormatter'

			:return formatter.format return value

			:raises AssertionError: When the method is not supported.
		"""
		# format the results using the selected formatter
		return formatter( self.results ).format( *metrics )

def show( args ):
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

	# check if any formatting options were given
	if args.plot:
		from dummy.viewer.formatters import PlotFormatter
		formatter = PlotFormatter
	else:
		from dummy.viewer.formatters import LogFormatter
		formatter = LogFormatter

	# format them in some way
	manager.format( metrics=args.metric, formatter=formatter )
