import logging
import dummy.models import TestResult

logger = logging.getLogger( __name__ )

class Formatter:
	def __init__( self, testresults ):
		self.testresults = testresult

	def format( self, *metrics ):
		raise NotImplementedError( "Not implemented" )

class LoggerFormatter( Formatter ):
	def __init__( self, testresults ):
		super( LoggerFormatter, self ).__init__( testresults )

	def format( self, *metrics ):
		for testresult in self.testresults:
			logger.info( "Results for test `%s` at commit %s" % ( testresult.test.name, testresult.commit ))
			logger.info( "Test started at `%s`" % testresult.started )
			logger.info( "Test completed at `%s`" % testresult.completed )

			# Format metrics
			# If no metrics given, format all metrics
			# Note: You cannot do metrics = testresult.metrics, because of th next loop.
			if len( metrics ) == 0:
				for metric_name in testresult.metrics:
					output_metric( testresult, metric_name )
			else:
				for metric_name in metrics:
					output_metric( testresult, metric_name )

	def output_metric( self, testresult, metric_name ):
		if metric_name in testresult.metrics:
			metric = testresult.metrics[ 'metric_name' ]
			logger.info( "Metric `%s` : %s" % ( metric_name, metric ))
		else:
			logger.warn( "This result does not contain metric `%s`." % metric_name )
