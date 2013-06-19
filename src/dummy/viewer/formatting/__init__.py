class ResultFormatter( object ):

	def format_results( self, results ):
		for r in results:
			self.format_entry( r )

	def format_entry( self, entry ):
		""" Format a single entry according to Formatter implementation.
		"""
		raise NotImplementedError( "Not implemented" )

	def format( self, entries ):
		raise NotImplementedError( "This formatter can only be used to format TestResults" )

class Formatter( ResultFormatter ):
	""" A Formatter outputs dicts in a certain format.
	"""

	def __init__( self, *args, **kwargs ):
		pass

	def format_results( self, results, *metrics ):
		# per default we serialize the results as dicts
		# and pass it to the normal formattr
		serialized = [ s.serialize() for s in results ]

		# filter the metrics
		for org, s in zip( results, serialized ):
			# Format metrics
			# If no metrics given, format all metrics
			# Note: You cannot do metrics = testresult.metrics, because of th next loop.
			if len( metrics ) == 0:
				dometrics = s[ 'metrics' ].keys()
			else:
				dometrics = metrics

			s[ 'metrics' ] = { key: org.get_metric( key ) for key in dometrics }

		return self.format( serialized )

	def format( self, entries ):
		""" Format a list of items or a single item entries
		"""
		if type( entries ) != list:
			l = [ entries ]

		concat = []
		for i in entries:
			formatted = self.format_entry( i )

			if formatted is not None:
				concat.append( formatted )

		return concat

from dummy.viewer.formatting.streamformatters import *
from dummy.viewer.formatting.plotformatters import *
