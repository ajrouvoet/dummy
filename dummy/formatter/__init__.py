import logging
import json
import re

from termcolor import colored

from dummy.models import TestResult

__all__ = ( 'Formatter', 'LogFormatter' )

# configure the results logger
logger = logging.getLogger( "resultformatter" )
logger.setLevel( logging.INFO )
ch = logging.StreamHandler()
logger.addHandler( ch )

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
		raise NotImplementedError( "Not implemented" )

class LogFormatter( Formatter ):

	def format( self, *metrics ):
		for testresult in self.testresults:
			title = colored( "%s (%s)" % ( testresult.test.name, testresult.commit ), 'green' )

			logger.info( len( title ) * "-" )
			logger.info( title )
			logger.info( len( title ) * "-" )
			logformatter.indent()
			logger.info( colored( 'started', 'white' ) + ": %s" % testresult.started )
			logger.info( colored( 'completed', 'white' ) + ": %s" % testresult.completed )

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
		if metric_name in testresult.metrics:
			metric = testresult.metrics[ metric_name ]

			if type( metric ) in [ dict, list ]:
				logger.info( colored( "%s" % metric_name, 'white' ) + ":" )
				logformatter.indent()
				logger.info( json.dumps( metric, indent=4 ))
				logformatter.unindent()
			else:
				logger.info( colored( "%s" % metric_name, 'white' ) + ": %s" %  metric )
		else:
			logger.warn( "This result does not contain metric `%s`." % metric_name )
