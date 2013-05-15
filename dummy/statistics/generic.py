import logging
from dummy.statistics import Engine

logger = logging.getLogger( __name__ )

class CountEngine( Engine ):

	def __init__( self, metric ):
		assert len( metric ) > 0, "CountEngine requires a metric name"
		super( CountEngine, self ).__init__( metric )

		self.passing = 0
		self.total = 0

	def get_result( self ):
		return {
			'passing': self.passing,
			'total': self.total
		}

	def process( self, data ):
		if data == "PASS":
			self.passing += 1

		self.total += 1
