import json

class Collector:
	""" Abstract base class Collector
	"""

	# output types
	VALUE = 'value'
	JSON = 'json'

	TYPE_CHOICES = ( VALUE, JSON )

	def __init__( self, type="value" ):
		assert type in Collector.TYPE_CHOICES, "Unknown collector type: `%s`" % type
		self.type = type

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
				raise ValueError( "Collector `%s` did not return valid JSON: %s" % ( self.path,
				str( e )))

		return output
