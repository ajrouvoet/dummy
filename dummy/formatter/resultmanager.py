from dummy.formatter import LoggerFormatter

class ResultManager:
	LOGGER = "logger"
	FORMAT_METHOD = ( LOGGER )

	def __init__( self, results ):
		self.results = results

	def add_result( self, result ):
		self.results.append( result )

	def format( self, method="logger", *metrics ):
		assert method in TestResultFormatter.FORMAT_METHOD, "Unknown format method: `%s`" % method

		#Select a Formatter
		if method is LOGGER:
			formatter = LoggerFormatter()


		formatter.format( *metrics )