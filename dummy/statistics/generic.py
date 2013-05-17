import logging
from dummy.statistics import Engine

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

class CoverageOverviewEngine( Engine ):

	def __init__( self, metric="coverage" ):
		super( CoverageOverviewEngine, self ).__init__( metric )

		self.coverage = {
			'lines_percentage' : 0,
			'function_percentage' : 0 
		}

	def get_result( self ):
		return self.coverage

	def process( self, data ):
		""" Process the coverage data

			raises:
				KeyError: When the coverage data is wrongly formatted.
		"""
		lines = 0
		lines_hit = 0
		functions = 0
		functions_hit = 0
		for value in data.itervalues():
			try:
				functions += value[ 'functions' ]
				functions_hit += value[ 'functions_hit' ]
				lines += value[ 'lines' ]
				lines_hit += value[ 'lines_hit' ]
			except KeyError as e:
				raise KeyError( "Wrongly formatted data for CoverageOverviewEngine: %s" % str( e ))

		self.coverage[ 'lines_percentage' ] = lines_hit / lines * 100 if lines > 0 else 0
		self.coverage[ 'lines_percentage' ] = functions_hit / functions * 100 if functions > 0 else 0