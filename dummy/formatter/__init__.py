import logging
import json
import re

import pylab #Pylab is unused except for plotting.
from termcolor import colored

from dummy.models import TestResult

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
		metric = testresult.get_metric( metric_name ) # metrics[ metric_name ]

		if type( metric ) in [ dict, list ]:
			printer.info( colored( "%s" % metric_name, 'white' ) + ":" )
			logformatter.indent()
			printer.info( json.dumps( metric, indent=4 ))
			logformatter.unindent()
		else:
			printer.info( colored( "%s" % metric_name, 'white' ) + ": %s" %  metric )

class PlotFormatter( Formatter ):
	""" The PlotFormatter outputs tests results to a plot.
	"""

	def format( self, *metrics ):
		# create the figure
		fig = pylab.figure( facecolor='white' )

		# get the xlabels
		x = range( 1, len( self.testresults ) + 1 )
		xlabels = [ t.test.name for t in self.testresults ]

		pylab.title( 'Metric values per test (commit: %s)' % self.testresults[0].commit, fontsize=22 )
		pylab.legend()
		pylab.xticks( rotation=20 )
		pylab.grid( True, markevery='integer' )
		pylab.xlabel( 'tests', fontsize=16 )
		pylab.margins( 0.05 )
		pylab.xticks( x, xlabels )

		# create the plots
		for metric in metrics:
			self.format_metric( metric )

		# and show it
		pylab.show()

	def format_metric( self, metric ):
		""" Process a single metric in all testresults.
		"""
		x = range( 1, len( self.testresults ) + 1 )
		y = [ t.get_metric( metric ) for t in self.testresults ]

		try:
			plot = pylab.plot( x, y )
			pylab.setp( plot,
				label=metric,
				linewidth=2.0,
				marker=".",
				markersize=8.0,
				aa=True
			)
		except TypeError as e:
			raise Exception(
				"The metric `%s` is not numeric and can thus not be plotted." % metric
			)

class ResultManager:
	LOG = "log"
	PLOT = "plot"
	FORMAT_METHODS = ( LOG, PLOT )

	def __init__( self, results ):
		self.results = results

	def add_result( self, result ):
		""" Add a TestResult to this ResultManager.
		"""
		self.results.append( result )

	def format( self, method, *metrics ):
		""" Format the results into the specified format.

			Supported methods: `log`, `plot`.

			Raises: AssertionError when the method is not supported.
		"""
		assert method in ResultManager.FORMAT_METHODS, "Unknown format method: `%s`" % method

		# select a Formatter
		if method is ResultManager.LOG:
			formatter = LogFormatter( self.results )
		elif method is ResultManager.PLOT:
			formatter = PlotFormatter( self.results )

		formatter.format( *metrics )
