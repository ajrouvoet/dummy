import logging
import sys

from dummy.viewer.formatting import Formatter, register
from dummy.utils import Printer
from termcolor import colored

__ALL__ = ( "LogFormatter" )

logger = logging.getLogger( __name__ )

# only do colored if stdout is a tty
# we check for stderr since we are using the logging module for all of this
if not sys.stdout.isatty():
	colored = lambda text, color: text

# configure the results logger
printer = logging.getLogger( "resultformatter" )
printer.setLevel( logging.INFO )
ch = logging.StreamHandler( sys.stdout )
printer.addHandler( ch )

class IndentLoggingFormatter( Printer, logging.Formatter ):

	INDENT = "|   "

	def __init__( self, indent=INDENT, *args, **kwargs ):
		logging.Formatter.__init__( self, *args, **kwargs )
		Printer.__init__( self, indent=indent )

	def format( self, record ):
		return self.msg( record.getMessage() )

logformatter = IndentLoggingFormatter( indent=colored( "|   ", "grey" ))
ch.setFormatter( logformatter )

@register( 'log' )
class LogFormatter( Formatter ):
	""" The LogFormatter outputs dicts to the logger.
	"""

	def format( self, items ):
		# homogenize list entries to dict
		if type( items ) == list:
			items = dict(( "item %d" % d, val ) for d, val in enumerate( items ))

		for title, entry in items.items():
			printer.info( len( title ) * "-" )
			printer.info( colored( title, 'green' ))
			printer.info( len( title ) * "-" )

			logformatter.indent()
			self.format_entry( entry )
			logformatter.unindent()

	def format_entry( self, entry ):
		# homogenize entry to dict
		if type( entry ) == list:
			entry = dict( enumerate( entry ))

		for key, value in sorted( entry.items() ):
			if type( value ) in ( list, dict ):
				printer.info( colored( "+ ", 'white' ) + colored( key, 'green' ) + ":" )
				logformatter.indent()
				self.format_entry( value )
				logformatter.unindent()
			else:
				printer.info( colored( key, 'white' ) + ": %s" % value )
