import os
import glob

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

class Metric:

	@classmethod
	def parse( cls, name, json ):
		assert len( name ) > 0
		assert json.get( 'collector' ) is not None, "Metric `%s` has no collector" % name

		return cls( name, Collector( json.get( 'collector' )) )

	def __init__( self, name, collector ):
		self.name = name

	def collect( self ):
		pass

