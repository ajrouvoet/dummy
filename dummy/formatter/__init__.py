import logging
import json
import re

from termcolor import colored

__all__ = ( 'Formatter', 'LogFormatter', 'ResultsManager' )

logger = logging.getLogger( __name__ )

# configure the results logger
printer = logging.getLogger( "resultformatter" )
printer.setLevel( logging.INFO )
ch = logging.StreamHandler()
printer.addHandler( ch )

class IndentFormatter( logging.Formatter ):

	INDENT = 4 * " "

	def __init__( self, *args, **kwargs ):
		super( IndentFormatter, self ).__init__( *args, **kwargs )

		self.indentation = 0

	def indent( self ): self.indentation += 1
	def unindent( self ):
		if self.indentation > 0:
			self.indentation -= 1

	def format( self, record ):
		message = []

		for line in record.getMessage().splitlines():
			message.append( self.indentation * IndentFormatter.INDENT + line )

		return "\n".join( message )

logformatter = IndentFormatter()
ch.setFormatter( logformatter )

class Formatter( object ):

	def __init__( self, testresults ):
		self.testresults = testresults

	def format( self, *metrics ):
		""" Format the given metrics according to Formatter implementation.
		"""
		raise NotImplementedError( "Not implemented" )

class LogFormatter( Formatter ):
	""" The LogFormatter outputs TestResults to the logger.
	"""

	def format( self, *metrics ):
		for testresult in self.testresults:
			title = colored( "%s (%s)" % ( testresult.test.name, testresult.commit ), 'green' )

			printer.info( len( title ) * "-" )
			printer.info( title )
			printer.info( len( title ) * "-" )
			logformatter.indent()
			printer.info( colored( 'started', 'white' ) + ": %s" % testresult.started )
			printer.info( colored( 'completed', 'white' ) + ": %s" % testresult.completed )

			# Format metrics
			# If no metrics given, format all metrics
			# Note: You cannot do metrics = testresult.metrics, because of th next loop.
			if len( metrics ) == 0:
				for metric_name in testresult.metrics:
					self.format_metric( testresult, metric_name )
			else:
				for metric_name in metrics:
					self.format_metric( testresult, metric_name )

			# go back to original indentation
			logformatter.unindent()

	def format_metric( self, testresult, metric_name ):
		""" Process a single metric of a testresult.
		"""
		logger.debug( "Processing metric `%s`" % metric_name )
		metric = testresult.get_metric( metric_name ) # metrics[ metric_name ]
		# Skip metrics with no associated metric results.
		if metric is None:
			logger.warn( "No associated metric result `%s` for test `%s`." \
			% (metric_name, testresult.test.name))
			return

		if type( metric ) in [ dict, list ]:
			printer.info( colored( "%s" % metric_name, 'white' ) + ":" )
			logformatter.indent()
			printer.info( json.dumps( metric, indent=4 ))
			logformatter.unindent()
		else:
			printer.info( colored( "%s" % metric_name, 'white' ) + ": %s" %  metric )

class ResultManager:
	def __init__( self, results ):
		self.results = results

	def add_result( self, result ):
		""" Add a TestResult to this ResultManager.
		"""
		self.results.append( result )

	def format( self, *metrics, **kwargs ):
		""" Format the results into the specified format.

			Supported methods: `log`, `plot`.

			Raises: AssertionError when the method is not supported.
		"""
		# default the formatter
		formatter = kwargs.get( 'formatter', LogFormatter )

		# format the results using the selected formatter
		formatter( self.results ).format( *metrics )
