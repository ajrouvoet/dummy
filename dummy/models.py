import os
import glob
import logging
from datetime import datetime

from dummy import config
from dummy.utils import subprocess, create_dir, plugin_environ
from dummy.collector import Collector

logger = logging.getLogger( __name__ )

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
		self._metrics = {}
		self.start_time = None
		self.stop_time = None

		assert os.path.exists( self.path ), "Sorry, could not find the test `%s`" % name

	def log_path( self ):
		return os.path.join( config.TEST_OUTPUT_DIR, "%s.log" % self.name )

	def run( self ):
		self.start_time = datetime.now()
		output = subprocess([ config.TEST_RUNNER, self.path ], test=self )
		self.stop_time = datetime.now()
		path = self.log_path()

		# write the test output temporarily to a file
		# for the collectors to use
		create_dir( path )
		with open( path, 'w' ) as fh:
			fh.write( output )

		return output

	def run_metric( self, metric ):
		self._metrics[ metric.name ] = metric.collect( self )

		return self._metrics[ metric.name ]

	@property
	def metrics( self ):
		return self._metrics

	def get_metric( self, name ):
		return self._metrics[ name ]

	def serialize( self ):
		""" Serialize self to dictionary
		"""

		result = {}
		result['name'] = self.name
		result['started'] = self.start_time
		result['completed'] = self.stop_time

		metrics = {}
		for metric in self.metrics:
			metrics[metric.key()] = metric.value()
		result['metrics'] = metrics
		
		return result

	def target_dir( self ):
		return config.TARGET_DIR + self.name

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

	def collect( self, test, env={} ):
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

		assert len( name ) > 0
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
		assert isinstance( collector, Collector ), \
			"Metric constructor collector must be of type Collector"

		self.name = name
		self.collector = collector

	def collect( self, test ):
		return self.collector.collect( test, env=plugin_environ() )
