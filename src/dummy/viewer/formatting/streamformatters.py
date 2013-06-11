import logging
import sys

from dummy.viewer.formatting import Formatter
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

class IndentLoggingFormatter( logging.Formatter ):

	INDENT = "|   "

	def __init__( self, indent=INDENT, *args, **kwargs ):
		super( IndentLoggingFormatter, self ).__init__( *args, **kwargs )

		self.indentation = 0
		self._indentstr = indent

	def indent( self ): self.indentation += 1
	def unindent( self ):
		if self.indentation > 0:
			self.indentation -= 1

	def format( self, record ):
		message = []

		for line in record.getMessage().splitlines():
			message.append( self.indentation * self._indentstr + line )

		return "\n".join( message )

logformatter = IndentLoggingFormatter( indent=colored( "|   ", "grey" ))
ch.setFormatter( logformatter )

class LogFormatter( Formatter ):
	""" The LogFormatter outputs TestResults to the logger.
	"""

	def format( self, entry ):
		title = colored( self.title.format( **entry ), 'green' )

		printer.info( len( title ) * "-" )
		printer.info( title )
		printer.info( len( title ) * "-" )
		logformatter.indent()

		self._format_body( entry )

		# go back to original indentation
		logformatter.unindent()

	def _format_body( self, entry ):
		for key, value in sorted( entry.items() ):
			if type( value ) == dict:
				printer.info( colored( "+ ", 'white' ) + colored( key, 'green' ) + ":" )
				logformatter.indent()
				self._format_body( value )
				logformatter.unindent()
			else:
				printer.info( colored( key, 'white' ) + ": %s" % value )
