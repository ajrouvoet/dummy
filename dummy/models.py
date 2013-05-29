import os
import glob
import logging
import dateutil.parser
from datetime import datetime

from dummy.config import config, settings
from dummy.utils import io, git, subp
from dummy.collector import Collector

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
				commit=data[ 'commit' ]
			)

			if 'metrics' in data:
				result.metrics = data[ 'metrics' ].copy()

			return result
		except KeyError as e:
			raise KeyError( "Unproper dictionary given to unserialize as TestResult: %s", str( e ))

	def __init__( self, test, start, stop, commit=None ):
		assert start is not None
		assert stop is not None

		self.test = test
		self.started = start
		self.completed = stop
		self.commit = commit or git.describe()
		self.metrics = {}

		# additional test result files by name
		self.files = {}

	def storage_dir( self ):
		return settings.STORAGE_DIR( self.test, self.commit )

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
		self.env_cache = None

		assert os.path.exists( self.path ), "Sorry, could not find the test `%s`" % name

	def log_path( self ):
		return os.path.join( config.TEST_OUTPUT_DIR, "%s.log" % self.name )

	def env( self ):
		""" return:
				{dict}: the test specific environment
		"""
		# cache the environment
		if self.env_cache is None:
			self.env_cache = subp.plugin_environ( test=self )

		return self.env_cache

	def run( self, metrics=[] ):
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
		result = TestResult( self, start, stop )
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
		# run the collector script with working directory the test folder.
		abspath = os.path.abspath( test.path ).encode( 'string-escape' )
		output = subp.subprocess([ os.path.abspath( self.path ), test.name ], test=test, cwd=abspath )

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
