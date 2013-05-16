from dummy import config
from dummy.models import Test, Metric
from dummy.storage import Storage
from dummy.statistics import Statistic

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

		# load the metric and statistic instances from the config
		self.load_metrics()
		self.load_statistics()

	def add_test( self, test ):
		self.queue.append( test )

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

	def pre_test_hook( self, test ):
		for name, metric in self.metrics.items():
			metric.pre_test_hook( test )

	def run_test( self, test ):
		logger.info( 80*"-" )

		# run the pre test hooks
		logger.info( "Running pre-test hooks..." )
		self.pre_test_hook( test )

		# run the test
		# and save the TestResult
		logger.info( "Running test: `%s`" % test.name )
		self.results.append( test.run( self.metrics.values() ))

		# complete it
		self.completed.append( test )
		logger.info( "100% complete" )

	def gather_statistics( self, stats=None ):
		# default stats to all configured stats
		if stats is None: stats = self.statistics

		for s in stats.values():
			self.gathered_stats[ s.name ] = s.gather( self.results )
			logger.info( "Gathered statistic `%s`: %s" % ( s.name, self.gathered_stats[ s.name ]))

	def run( self ):
		""" run the tests in the queue
		"""
		self.clean()

		while len( self.queue ) != 0:
			test = self.queue.pop()
			self.run_test( test )

	def store( self ):
		Storage( self ).store()

# subprogram run
def run( args ):
	name = args.name
	runner = Runner()

	# discover the tests we need to run and add them to the runner
	# check if we need to run a whole test suite
	if args.suite:
		# make sure to have a valid test suite name
		suite = config.SUITES.get( name )
		assert suite is not None,\
			"We looked, but a test suite with name `%s` was not found." % name

		logger.info( "Running test-suite `%s`" % name )
		for name in suite:
			for fname in Test.glob( name ):
				runner.add_test( Test( fname ))

	# if not running a whole suite
	# just queue the one named test
	else:
		runner.add_test( Test( name ))

	# run the tests
	runner.run()

	# gather the statistics as configured
	runner.gather_statistics()

	# store the results
	if args.store:
		runner.store()
