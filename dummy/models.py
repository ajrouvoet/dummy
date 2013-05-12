import os
import glob
import json
import logging

from dummy import config
from dummy.utils import subprocess, create_dir

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

		assert os.path.exists( self.path ), "Sorry, could not find the test `%s`" % name

	def log_path( self ):
		return os.path.join( config.TEST_OUTPUT_DIR, "%s.log" % self.name )

	def run( self ):
		output = subprocess([ config.TEST_RUNNER, self.path ], test=self )
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

class Collector:
	""" Abstract base class Collector
	"""

	# output types
	VALUE = 'value'
	JSON = 'json'

	TYPE_CHOICES = ( VALUE, JSON )

	def collect( self, test ):
		raise NotImplementedError( "Not implemented" )

	def parse_output( self, output ):
		""" Parse the output of the collection script if necessary

			returns:
				parsed output or unchanged output if type == VALUE
		"""
		if self.type == Collector.JSON:
			try:
				output = json.loads( output )
			except ValueError as e:
				raise ValueError( "Collector `%s` did not return valid JSON" % self.path )

		return output
		
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

		if isinstance(coll, str):
			#If it is a string, then it's a path to a script.
			return cls(
			name,
			collector=Script( coll, type=output_type )
			)
		else:
			return cls(name, coll)

	def __init__( self, name, collector ):
		assert isinstance( collector, Collector ), \
			"Metric constructor collector must be of type Collector"

		self.name = name
		self.collector = collector

	def collect( self, test ):
		return self.collector.collect( test )
		
