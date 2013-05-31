import os
import glob
import logging
import dateutil.parser
from datetime import datetime

from dummy import config
from dummy.utils import io, git, subp
from dummy.runner.collectors import Collector
from dummy.runner.collectors.generic import ScriptCollector

logger = logging.getLogger( __name__ )

class TestResult:
	""" Stores the result from executing a test
	"""

	@classmethod
	def unserialize( cls, test, data ):
		""" Unserializes a dictionary to a TestResult.
			This only works well if dict is formatted according to the serialize() method.

			raises:
				KeyError: When data does not contain 'name', 'started' and 'completed' keys.
		"""

		# Assume that name, started and completed are in dict.
		try:
			result = cls(
				test,
				start=dateutil.parser.parse( data[ 'started' ]),
				stop=dateutil.parser.parse( data[ 'completed' ]),
				target=dateutil.parser.parse( data[ 'target' ]),
				commit=data[ 'commit' ]
			)

			if 'metrics' in data:
				result.metrics = data[ 'metrics' ].copy()

			return result
		except KeyError as e:
			raise KeyError( "Unproper dictionary given to unserialize as TestResult: %s", str( e ))

	def __init__( self, test, start, stop, target, commit=None ):
		assert start is not None
		assert stop is not None

		self.test = test
		self.started = start
		self.completed = stop
		self.target = target
		self.commit = commit or git.describe()
		self.metrics = {}

		# additional test result files by name
		self.files = {}

	def storage_dir( self ):
		return config.STORAGE_DIR( self.test, self.commit )

	def log( self, logdata ):
		""" log the logdata to the results log file
		"""
		# get the output log path
		path = self.test.log_path()

		# write the test output temporarily to a file
		# for the collectors to use
		io.create_dir( path )
		with open( path, 'w' ) as fh:
			fh.write( logdata )

	def add_metric( self, metric, value ):
		self.metrics[ metric.name ] = value

	def get_metric( self, name ):
		""" Gets a metric by it's (dotted) name.
			e.g: get_metric( 'coverage.functions.State_create' )

			return:
				{any}: value of the metric, or None if not listed
		"""
		# split the name into parts
		names = name.split( '.' )

		try:
			value = self.metrics
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
		result[ 'started' ] = self.started.isoformat( " " )
		result[ 'completed' ] = self.completed.isoformat( " " )
		result[ 'target' ] = self.target
		result[ 'metrics' ] = self.metrics.copy()
		result[ 'commit' ] = self.commit

		return result

	def __str__( self ):
		return "`%s` result" % self.test.name

class Test:

	@staticmethod
	def glob( name ):
		path = os.path.join( config.TESTS_DIR, name )
		matches = glob.glob( path )

		# now remove the path prefix
		test_paths = [ m[ (len( config.TESTS_DIR)+1): ] for m in matches ]
		if len( test_paths ) == 0:
			logger.error( "Did not find any tests associated with name `%s`" % name )
		return test_paths

	def __init__( self, name ):
		""" raises:
				AssertionError - 	if the test was not found in the TESTS_DIR
									or if the name was of zero length
		"""
		assert len( name ) > 0

		self.name = name
		self.path = os.path.join( config.TESTS_DIR, name )

		assert os.path.exists( self.path ), "Sorry, could not find the test `%s`" % name

	def log_path( self ):
		return os.path.join( config.TEST_OUTPUT_DIR, "%s.log" % self.name )

	def env( self ):
		""" return:
				{dict}: the test specific environment
		"""
		return subp.plugin_environ( test=self )

	def run( self, target, metrics=[] ):
		""" Run this Test.

			raises:
				IOError: Unable to write output to file in log directory.

			return:
				{string}: The test output.
		"""
		# run the actual test
		start = datetime.now()
		output = subp.subprocess([ config.TEST_RUNNER, self.path ], test=self )
		stop = datetime.now()

		# create a result instance
		result = TestResult( self, start, stop, target )
		result.log( output.encode( 'utf8' ))

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

class Metric:

	@classmethod
	def parse( cls, name, conf ):
		""" Parse a metric instance from a metric configuration dictionary

			return:
				Metric instance
		"""
		collname = conf.get( 'collector' )
		script = conf.get( 'script' )
		output_type = conf.get( 'type', Collector.VALUE )

		assert collname is not None or script is not None,\
			"Metric `%s` neither has a collector, nor a script" % name

		if collname is not None:
			kwargs = conf.get( 'kwargs', {} )
			args = conf.get( 'args', [] )

			# try to import the collector
			try:
				mod, clsname = collname.rsplit( '.', 1 )
				logger.debug( collname )
				logger.debug( mod )
				logger.debug( clsname )
				mod = __import__( mod, fromlist=[ clsname ] )
				coll = getattr( mod, clsname )
			except ImportError as e:
				logger.error( "Could not import the collector `%s`" % collname )
				raise e

			# try to initiate the collector
			try:
				coll = coll( *args, **kwargs )
			except TypeError:
				logger.error( "Could not instantiate the collector `%s`" % collname )
				raise e
		else:
			coll = ScriptCollector( script, type=output_type )

		return cls( name, collector=coll )

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
