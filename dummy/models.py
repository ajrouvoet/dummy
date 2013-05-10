import os
import glob
import json

from dummy import config
from dummy.utils import subprocess

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
		assert os.path.exists( self.path ), "Sorry, could not find the test `%s`" % name

		# readonly property
		self._output = None

	@property
	def output( self ): return self._output

	def run( self ):
		self._output = subprocess([ config.TEST_RUNNER, self.path ])

		return self.output

class Collector:

	# output types
	VALUE = 'value'
	JSON = 'json'

	TYPE_CHOICES = ( VALUE, JSON )

	def __init__( self, path, type='value' ):
		assert type in Collector.TYPE_CHOICES, "Unknown collector type: `%s`" % type

		self.path = path
		self.type = type

	def collect( self, test ):
		assert os.path.exists( self.path ), "Could not find the collector script: %s" % self.path

		return self.parse_output( subprocess([ self.path, test.name ]))

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

		return cls(
			name,
			collector=Collector( coll, type=output_type )
		)

	def __init__( self, name, collector ):
		assert isinstance( collector, Collector ), \
			"Metric constructor collector must be of type Collector"

		self.name = name
		self.collector = collector
