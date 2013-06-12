import os
import glob
import logging
from subprocess import check_call, PIPE, CalledProcessError

from dummy.statistics import Engine
from dummy import config
from dummy.runner.collectors.generic import CCoverageCollector
from dummy.utils import lcov

logger = logging.getLogger( __name__ )

class CountEngine( Engine ):

	def __init__( self, metric ):
		assert len( metric ) > 0, "CountEngine requires a metric name"
		super( CountEngine, self ).__init__( metric )

		self.bars = {
			'total': 0
		}

	def get_result( self ):
		return self.bars

	def process( self, data ):
		if self.bars.get( data ) is None:
			self.bars[ data ] = 1
		else:
			self.bars[ data ] += 1

		self.bars[ 'total' ] += 1

class KeyValueCountEngine( Engine ):

	def __init__( self, metric ):
		assert len( metric ) > 0, "KeyValueCountEngine requires a metric name"
		super( KeyValueCountEngine, self ).__init__( metric )

		self.bars = {
			'total': 0
		}

	def get_result( self ):
		return self.bars

	def process( self, data ):
		try:
			for key, value in data.items():
				self.bars[ key ] = self.bars.get( key, 0 ) + int( value )
				self.bars[ 'total' ] += int( value )
		except TypeError as e:
			logger.error( "Badly formatted rulestat result file." )
			raise

class CCoverageOverviewEngine( Engine ):

	def __init__( self ):
		super( CCoverageOverviewEngine, self ).__init__( metric=None )

		self.collectpath = os.path.join( config.TEMP_DIR, "coverage_collect.info" )
		self.paths = []

	def run( self, *args, **kwargs ):
		# create the baseline
		logger.debug( "Creating coverage baseline" )
		lcov.baseline( self.collectpath )

		return super( CCoverageOverviewEngine, self ).run( *args, **kwargs )

	def get_result( self ):
		# map paths to options for lcov
		opts = []

		for path in self.paths:
			opts += [ '-a', path ]

		# combine the data with the accumulated set
		try:
			logger.info(
				[ 'lcov', '-a', self.collectpath ] + opts + [ '-o', self.collectpath ]
			)
			proc = check_call(
				[ 'lcov', '-a', self.collectpath ] + opts + [ '-o', self.collectpath ],
				stdout=PIPE,
				stderr=PIPE
			)
		except CalledProcessError as e:
			logger.error( "lcov aggregation failed for test `%s`" % result.test.name )
			raise

		with open( self.collectpath ) as fh:
			# parse the accumulated data
			results = lcov.parse( fh.read() )

		return results

	def process( self, result ):
		# create the path
		path = os.path.join( config.STORAGE_DIR( result.test, result.commit ),
			CCoverageCollector.FILENAME )

		# check if it exists
		if not os.path.exists( path ):
			logger.warn( "Result for test %s has no coverage data attached" % str( result ) )
		else:
			self.paths.append( path )
