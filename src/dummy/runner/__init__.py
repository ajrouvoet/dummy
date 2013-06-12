from dummy.utils import git, io, argparser
from dummy import config
from dummy.models import Test
from dummy.runner.models import Metric
from dummy.statistics import Statistic
from dummy.storage import JsonStorageProvider

import os
import glob
import subprocess
import logging
import shutil
import datetime

logger = logging.getLogger( __name__ )

class Runner:

	def __init__( self ):
		self.tests = [] # list of queued tests
		self.metrics = {} # list of metrics to collect
		self.results = [] # list of TestResult instances obtained
		self.statistics = {} # list of statistics to collect
		self.gathered_stats = {} # list of gathered statistics

		# assert no lock is set
		assert not os.path.exists( config.LOCK_FILE ), \
			"A dummy lock file exists. " +\
			"If you are sure dummy is not already running" +\
			", you can rm the `%s` file" % config.LOCK_FILE

		# clean the runtime env
		self.clean()

		# load the metric and statistic instances from the config
		self.load_metrics()
		self.load_statistics()

	def add_test( self, test ):
		self.tests.append( test )

	def load_metrics( self ):
		logger.info( "Loading metrics..." )

		for name, metric in config.METRICS.items():
			logger.debug( "Loading metric `%s`" % name )

			m = Metric.parse( name, metric )
			self.metrics[ name ] = m

	def load_statistics( self ):
		logger.info( "Loading statistics..." )

		for name, statistic in config.STATISTICS.items():
			logger.debug( "Loading statistic `%s`" % name )

			s = Statistic.parse( name, statistic )
			self.statistics[ name ] = s

	def clean( self ):
		logger.debug( "Cleaning `%s`" % config.TEMP_DIR )
		if os.path.isdir( config.TEMP_DIR ):
			shutil.rmtree( config.TEMP_DIR )

		# make the tmp directory for use
		io.create_dir( os.path.join( config.TEMP_DIR, "bla" ))

	def _pre_test_hook( self, test ):
		for name, metric in self.metrics.items():
			metric.pre_test_hook( test )

	def _gather_statistics( self, stats=None ):
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

	def run( self, target=config.DEFAULT_TARGET, commit=None, store=False ):
		# make sure we have work to do
		assert len( self.tests ) != 0, "No tests to run."

		# if a commit is given, we need to checkout out the commit
		# but keep the tests directory at the current branch
		try:
			# create a lock file to prevent multiple runners on the same repo
			with open( config.LOCK_FILE, 'w' ) as fh:
				fh.write( str( datetime.datetime.now() ))

			# checkout the correct commit
			if commit is not None:
				current = git.current_branch()

				# if not on any branch currently
				# remember the current commit
				if current == "HEAD":
					current = git.describe()

				logger.warning( "Checking out commit `%s`" % args.commit )
				git.checkout( args.commit )
				git.checkout( current, paths=config.TESTS_DIR )

			# actual running of the tests
			self._run_tests( target=target )

			# gather the statistics as configured
			self._gather_statistics()

			# store the results
			if store:
				self._store()
				logger.info( "Stored results!" )
			else:
				# TODO
				# ask the user if he wants to store the results
				pass

		# if a git error is caught while checking out the commit on
		# which to run the tests
		# we can't do anything
		except git.GitError as e:
			logger.error( "Could not checkout `%s`... Sorry!" % commit )
			raise

		finally:
			# make sure to always checkout the original commit again
			if commit is not None:
				try:
					git.checkout( current )
					logger.info( "Checked out the original HEAD again!" )
				except git.GitError as e:
					logger.error(
						"Could not checkout original branch... you'll have to do that yourself."
					)
					raise

			# make sure to remove the lock file
			io.remove_file( config.LOCK_FILE )

	def _run_tests( self, target ):
		""" run the tests in the queue
		"""
		total = len( self.tests )

		for i, test in enumerate( self.tests, 1 ):
			# run the pre test hooks
			logger.info( "Running pre-test hooks..." )
			self._pre_test_hook( test )

			# run the test
			# and save the TestResult
			logger.info( "Running test: `%s` [%d/%d]" % ( test.name, i, total ))

			try:
				self.results.append( test.run( target=target, metrics=self.metrics.values() ))
			except Test.RunError as e:
				logger.error( str( e ))

			logger.info( 80*"-" )

	def _store( self ):
		for result in self.results:
			JsonStorageProvider( result ).store()

		# copy the files from the temp results to the results
		temp_results_dir = os.path.join( config.TEMP_DIR, config.TARGET_DIR )
		for path, dirs, files in os.walk( temp_results_dir ):
			for f in files:
				abspath = os.path.join( path, f )
				relpath = os.path.relpath( abspath, config.TEMP_DIR )

				logger.debug( "Moving result file `%s`", relpath )

				io.create_dir( relpath )
				shutil.move( abspath, relpath )

		# After moving all the results files from the temp_results_dir, delete it.
		logger.debug( "Removing temporary results directory." )
		shutil.rmtree( temp_results_dir )

# subprogram run
def run( args ):
	# discover the tests and targets we need to run
	targets = argparser.discover_targets( args )
	tests = argparser.discover_tests( args )

	# run every target
	# this way we make sure the configuration is set correctly
	# during the whole execution of the program
	for i, t in enumerate( targets, 1 ):
		config.set_target( t )

		# create the runner
		runner = Runner()
		for test in tests:
			runner.add_test( test )

		logger.info( "Running tests for target `%s` [%d/%d]" % ( t, i, len( targets )))
		logger.info( 80*"-" )

		runner.run( store=args.store, target=t, commit=args.commit )
