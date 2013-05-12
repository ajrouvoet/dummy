from dummy.models import Collector

class Script(Collector):
	""" A class for running collector scripts.
	"""

	def __init__( self, path, type='value' ):
		assert os.path.exists( self.path ), "Could not find the collector script: %s" % self.path
		assert type in Collector.TYPE_CHOICES, "Unknown collector type: `%s`" % type

		self.path = path
		self.type = type

	def collect( self, test ):
		# run the collector script
		output = subprocess([ self.path, test.name ], test=test )

		# parse the output
		return self.parse_output( output )