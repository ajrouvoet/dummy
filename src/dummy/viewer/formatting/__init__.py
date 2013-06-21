import logging

__all__ = ( "Formatter", "ResultFormatter" )
logger = logging.getLogger( __name__ )

_formatters = dict()

def register( name ):
	logger.debug( "Formatter registered: %s" % name )
	def _reg( cls ):
		_formatters[ name ] = cls

		return cls

	return _reg

def find( name ):
	try:
		return _formatters[ name ]
	except KeyError:
		raise ValueError( "A formatter with name `%s` was not found" % name )

class Formatter( object ):
	""" A Formatter outputs dicts in a certain format.
	"""

	@staticmethod
	def get( name ): return find( name )

	@staticmethod
	def register( name ): return register( name )

	def __init__( self, *args, **kwargs ):
		pass

	def format_results( self, results, *metrics ):
		# per default we serialize the results as dicts
		# and pass it to the normal formatter
		serialized = { "%s (%s)" % ( s.test.name, s.commit ): s.serialize() for s in results }

		# filter the metrics
		for org, s in zip( results, serialized.values() ):
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
		""" Format a list of items
		"""
		concat = []
		for i in entries:
			formatted = self.format_entry( i )

			if formatted is not None:
				concat.append( formatted )

		return concat

class ResultFormatter( Formatter ):

	def format_results( self, results ):
		for r in results:
			self.format_entry( r )

	def format_entry( self, entry ):
		""" Format a single entry according to Formatter implementation.
		"""
		raise NotImplementedError( "Not implemented" )

from dummy.viewer.formatting.streamformatters import *
from dummy.viewer.formatting.plotformatters import *
from dummy.viewer.formatting.reportformatters import *
