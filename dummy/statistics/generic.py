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

	def __init__( self, metric="coverage.files" ):
		super( CoverageOverviewEngine, self ).__init__( metric )

		self.lines = 0
		self.lines_hit = 0
		self.functions = 0
		self.functions_hit = 0

	def get_result( self ):
		return {
			'lines_percentage': round(
					float( self.lines_hit ) / self.lines * 100
				) if self.lines > 0 else 0,
			'function_percentage': round(
					float( self.functions_hit ) / self.functions * 100
				) if self.functions > 0 else 0
		}

	def process( self, data ):
		""" Process the coverage data

			raises:
				KeyError: When the coverage data is wrongly formatted.
		"""
		for value in data.itervalues():
			try:
				self.functions += value[ 'functions' ]
				self.functions_hit += value[ 'functions_hit' ]
				self.lines += value[ 'lines' ]
				self.lines_hit += value[ 'lines_hit' ]
			except KeyError as e:
				raise KeyError( "Wrongly formatted data for CoverageOverviewEngine: %s" % str( e ))
