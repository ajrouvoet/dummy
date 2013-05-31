from dummy.utils import git, io
from dummy import config
from dummy.models import Test, Metric
from dummy.statistics import Statistic
from dummy.runner.storage import JsonStorageProvider
from dummy.formatter import ResultManager

import os
import glob
import subprocess
import logging
import shutil

logger = logging.getLogger( __name__ )

class Runner:

	def __init__( self ):
		self.queue = [] # list of queued tests
		self.completed = [] # list of completed tests
		self.metrics = {} # list of metrics to collect
		self.results = [] # list of TestResult instances obtained
		self.statistics = {} # list of statistics to collect
		self.gathered_stats = {} # list of gathered statistics

		# clean the runtime env
		self.clean()

		# load the metric and statistic instances from the config
		self.load_metrics()
		self.load_statistics()

	def add_test( self, test ):
		self.queue.append( test )

	def add_result( self, result ):
		self.results.append( result )

	def load_metrics( self ):
		for name, metric in config.METRICS.items():
			m = Metric.parse( name, metric )
			self.metrics[ name ] = m

			logger.debug( "Loaded metric `%s`" % m.name )

	def load_statistics( self ):
		for name, statistic in config.STATISTICS.items():
			s = Statistic.parse( name, statistic )
			self.statistics[ name ] = s

			logger.debug( "Loaded statistic `%s`" % s.name )

	def clean( self ):
		if os.path.isdir( config.TEMP_DIR ):
			shutil.rmtree( config.TEMP_DIR )

		# make the tmp directory for use
		io.create_dir( os.path.join( config.TEMP_DIR, "bla" ))
		logger.debug( "Cleaned `%s`" % config.TEMP_DIR )

	def pre_test_hook( self, test ):
		for name, metric in self.metrics.items():
			metric.pre_test_hook( test )

	def run_test( self, test ):
		# run the pre test hooks
		logger.info( "Running pre-test hooks..." )
		self.pre_test_hook( test )

		total_tests = len(self.queue) + len(self.completed)+1
		# run the test
		# and save the TestResult
		logger.info( "Running test: `%s` [%d/%d]" % (test.name, len(self.completed)+1, total_tests ))
		self.results.append( test.run( self.metrics.values() ))

		# complete it
		self.completed.append( test )
		logger.info( "100% complete" )

	def gather_statistics( self, stats=None ):
		# default stats to all configured stats
		if stats is None: stats = self.statistics

		logger.info( "Gathering statistics:" )
		for s in stats.values():
			self.gathered_stats[ s.name ] = s.gather( self.results )
			value = str( self.gathered_stats[ s.name ] ).strip()
			logger.info( "\t%s: %s" % (
				s.name,
				"%s ..." % value[:40] if len( value ) > 40 else value
			))

	def run( self ):
		""" run the tests in the queue
		"""
		logger.info( 80*"-" )

		while len( self.queue ) != 0:
			test = self.queue.pop()
			self.run_test( test )
			logger.info( 80*"-" )

	def store( self ):
		for result in self.results:
			JsonStorageProvider( result ).store()

		# copy the files from the temp results to the results
		for path, dirs, files in os.walk( os.path.join( config.TEMP_DIR, config.TARGET_DIR )):
			for f in files:
				abspath = os.path.join( path, f )
				relpath = os.path.relpath( abspath, config.TEMP_DIR )

				logger.debug( "Copying result file `%s`", relpath )

				io.create_dir( relpath )
				shutil.copyfile( abspath, relpath )

	def output( self, *metrics ):
		from dummy.formatter import LogFormatter

		resultmanager = ResultManager( self.results )
		resultmanager.format( *metrics, formatter=LogFormatter )

	def plot( self, *metrics ):
		from dummy.formatter.plotting import PlotFormatter

		resultmanager = ResultManager( self.results )
		resultmanager.format( *metrics, formatter=PlotFormatter )

def _discover_tests( args, runner ):
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
					runner.add_test( Test( fname ))
		except KeyError:
			logger.error( "We looked, but a test suite with name `%s` was not found." % name )

	# if not running a whole suite
	# just queue the named tests
	for names in [ Test.glob( name ) for name in args.tests ]:
		for name in names:
			runner.add_test( Test( fname ))

	return runner

# subprogram run
def run( args ):
	runner = Runner()

	# discover the tests we need to run and add them to the runner
	_discover_tests( args, runner )
	assert len( runner.queue ) != 0, "No tests to run."

	try:
		# if a commit is given, we need to checkout out the commit
		# but keep the tests directory at the current branch
		if args.commit is not None:
			current = git.current_branch()

			# if not on any branch currently
			# remember the current commit
			if current == "HEAD":
				current = git.describe()

			testpaths = [ t.path for t in runner.queue ]

			logger.warning( "Checking out commit `%s`" % args.commit )
			git.checkout( args.commit )
			git.checkout( current, paths=testpaths )

		# run the tests
		runner.run()

		# gather the statistics as configured
		runner.gather_statistics()

		# store the results
		if args.store:
			runner.store()
			logger.info( "Stored results!" )
		else:
			# TODO
			# ask the user if he wants to store the results
			pass
	finally:
		# always
		# recheckout the original branch
		# if necessary
		if args.commit is not None:
			try:
				git.checkout( current )
				logger.info( "Checked out the original HEAD again!" )
			except git.GitError as e:
				raise Exception(
					"Could not checkout original branch... you'll have to do that yourself. Sorry..."
				)

def show( args ):
	runner = Runner()

	commit = 'HEAD'
	if args.commit is not None:
		logger.debug( "Loading result from committish `%s`" % args.commit )
		commit = args.commit

	# discover the tests we need to run and add them to the runner
	_discover_tests( args, runner )

	for test in runner.queue:
		try:
			runner.add_result( JsonStorageProvider.load( commit, test ))
		except ValueError as e:
			logger.error( "No test results exists yet for test `%s`" % test.name )
			logger.debug( "Exception output: `%s`" % e )
	if args.plot:
		f = runner.plot
	else:
		f = runner.output

	if args.metric is not None:
		f( *args.metric )
	else:
		f( plot=args.plot )

# def quickstart( args ):
# 	logger.info( "Welcome to Dummy quickstart, where we configure your dummy_config.py" )
# 	logger.info( "Are you sure you wish to continue?" )
# 	choice = raw_input( "[y/n]" )
# 	if choice != "y":
# 		logger.warning( "Aborting..." )
#
# 	logger.info( "Copying default configuration to current directory." )
# 	(file, default_path, description) = imp.find_module( dummy.config.defaults )
# 	shutil.copy( default_path, 'dummy_config.py' )
