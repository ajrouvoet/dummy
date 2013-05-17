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
