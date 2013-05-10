from dummy import config
from dummy.models import Test, Metric

import os
import glob
import subprocess
import logging
import shutil

logger = logging.getLogger( __name__ )

class Runner:

	def __init__( self ):
		self.queue = []
		self.completed = []
		self.metrics = {}

		# load the metric instances from the config
		self.load_metrics()

	def add_test( self, test ):
		self.queue.append( test )

	def load_metrics( self ):
		for name, metric in config.METRICS.items():
			m = Metric.parse( name, metric )
			self.metrics[ name ] = m

			logger.debug( "Loaded metric `%s`" % m.name )

	def clean( self ):
		if os.path.isdir( config.TEMP_DIR ):
			shutil.rmtree( config.TEMP_DIR )

	def run( self ):
		""" run the tests in the queue
		"""
		self.clean()

		while len( self.queue ) != 0:
			test = self.queue.pop()

			# run the test
			logger.info( 80*"-" )
			logger.info( "Running test: `%s`" % test.name )
			test.run()

			# complete it
			self.completed.append( test )
			logger.info( "100%% complete" )

			# collect the metrics
			logger.info( "Metrics collected:" )
			for m in self.metrics.values():
				output = test.run_metric( m )
				logger.info( "\t%s: %s" % ( m.name, str( output ).strip() ))

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
