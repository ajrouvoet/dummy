import os
import glob
import logging
from datetime import datetime

from dummy import config
from dummy.utils import subprocess, create_dir, plugin_environ
from dummy.collector import Collector

logger = logging.getLogger( __name__ )

class TestResult:
	""" Stores the result from executing a test
	"""

	def __init__( self, test, start, stop, output ):
		assert start is not None
		assert stop is not None

		self.test = test
		self.start_time = start
		self.stop_time = stop
		self._metrics = {}

		self.log( output )

	def log( self, logdata ):
		""" Set stop time of test result to `now` and log the logdata to the results log file
		"""
		# get the output log path
		path = self.test.log_path()

		# write the test output temporarily to a file
		# for the collectors to use
		create_dir( path )
		with open( path, 'w' ) as fh:
			fh.write( logdata )

	def add_metric( self, metric, value ):
		self._metrics[ metric.name ] = value

	@property
	def metrics( self ):
		return self._metrics

	def get_metric( self, name ):
		""" Gets a metric by it's (dotted) name.
			e.g: get_metric( 'coverage.functions.State_create' )

			return:
				{any}: value of the metric, or None if not listed
		"""
		# split the name into parts
		names = name.split( '.' )

		try:
			value = self._metrics
			for name in names:
				value = value[ name ]
		except KeyError:
			value = None

		return value

	def serialize( self ):
		""" Serialize self to dictionary
		"""
		result = {}
		result[ 'name' ] = self.test.name
		result[ 'started' ] = self.start_time.isoformat( " " )
		result[ 'completed' ] = self.stop_time.isoformat( " " )
		result[ 'metrics' ] = self._metrics.copy()

		return result

class Test:

	@staticmethod
	def glob( name ):
		path = os.path.join( config.TESTS_DIR, name )
		matches = glob.glob( path )

		# now remove the path prefix
		return [ m[ (len( config.TESTS_DIR)+1): ] for m in matches ]

	def __init__( self, name ):
		""" raises:
				AssertionError - 	if the test was not found in the TESTS_DIR
									or if the name was of zero length
		"""
		assert len( name ) > 0

		self.name = name
		self.path = os.path.join( config.TESTS_DIR, name )
		self.env_cache = None

		assert os.path.exists( self.path ), "Sorry, could not find the test `%s`" % name

	def log_path( self ):
		return os.path.join( config.TEST_OUTPUT_DIR, "%s.log" % self.name )

	def storage_dir( self ):
		return os.path.join( config.TARGET_DIR, self.name )

	def target_dir( self ):
		return os.path.join( config.TARGET_DIR, self.name )

	def env( self ):
		""" return:
				{dict}: the test specific environment
		"""
		# cache the environment
		if self.env_cache is None:
			self.env_cache = plugin_environ( test=self )

		return self.env_cache

	def run( self, metrics=[] ):
		# run the actual test
		start = datetime.now()
		output = subprocess([ config.TEST_RUNNER, self.path ], test=self )
		stop = datetime.now()

		# create a result instance
		result = TestResult( self, start, stop, output )

		for metric in metrics:
			value = metric.collect( self )
			result.add_metric( metric, value )

			# log the collection of the metric
			output = str( value ).strip()
			logger.info( "\t%s: %s" % (
				metric.name,
				"%s ..." % output[:40] if len( output ) > 40 else output
			))

		return result

class Script( Collector ):
	""" A class for running collector scripts.
	"""

	def __init__( self, path, type='value' ):
		super( Script, self ).__init__( type=type )

		assert os.path.exists( path ), "Could not find the collector script: %s" % path
		assert type in Collector.TYPE_CHOICES, "Unknown collector type: `%s`" % type

		self._path = path

	@property
	def path( self ):
		return self._path

	def collect( self, test ):
		# run the collector script
		output = subprocess([ self.path, test.name ], test=test )

		# parse the output
		return self.parse_output( output )

class Metric:

	@classmethod
	def parse( cls, name, conf ):
		""" Parse a metric instance from a metric configuration dictionary

			return:
				Metric instance
		"""
		coll = conf.get( 'collector' )

		assert coll is not None, "Metric `%s` has no collector" % name

		output_type = conf.get( 'type', Collector.VALUE )

		if isinstance( coll, Collector ):
			# if it is a class, initiate it as a collector
			return cls( name, collector=coll )
		else:
			# if it is a string, then it's a path to a script.
			return cls(
				name,
				collector=Script( coll, type=output_type )
			)

	def __init__( self, name, collector ):
		assert len( name ) > 0, "A metric must be named"
		assert isinstance( collector, Collector ), \
			"Metric constructor collector must be of type Collector"

		self.name = name
		self.collector = collector

	def pre_test_hook( self, test ):
		self.collector.pre_test_hook( test )

	def collect( self, test ):
		return self.collector.collect( test )
