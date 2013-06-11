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
		super( CountEngine, self ).__init__( metric )

		self.bars = {
			'total': 0
		}

	def get_result( self ):
		return self.bars

	def process( self, data ):
		for key, value in data:
			self.bars[ key ] = self.bars.get( key, 0 ) + value
			self.bars[ 'total' ] += value

class CCoverageOverviewEngine( Engine ):

	def __init__( self ):
		super( CCoverageOverviewEngine, self ).__init__( metric=None )

		self.path = os.path.join( config.TEMP_DIR, "coverage_collect.info" )

	def run( self, *args, **kwargs ):
		# create the baseline
		logger.debug( "Creating coverage baseline" )
		lcov.baseline( self.path )

		return super( CCoverageOverviewEngine, self ).run( *args, **kwargs )

	def get_result( self ):
		with open( self.path ) as fh:
			# parse the accumulated data
			results = lcov.parse( fh.read() )

		return results

	def process( self, result ):
		path = os.path.join( result.test.env()[ 'RESULTS_DIR' ], CCoverageCollector.FILENAME )

		# combine the data with the accumulated set
		try:
			proc = check_call([ 'lcov',
				'-a', self.path,
				'-a', path,
				'-o', self.path
			], stdout=PIPE, stderr=PIPE )
		except CalledProcessError as e:
			logger.error( "lcov aggregation failed for test `%s`" % result.test.name )

			raise

