from dummy.formatter import LoggerFormatter

class ResultManager:
	LOGGER = "logger"
	FORMAT_METHOD = ( LOGGER )

	def __init__( self, results ):
		self.results = results

	def add_result( self, result ):
		self.results.append( result )

	def format( self, method="logger", *metrics ):
		assert method in ResultManager.FORMAT_METHOD, "Unknown format method: `%s`" % method

		#Select a Formatter
		if method is ResultManager.LOGGER:
			formatter = LoggerFormatter( self.results )


		formatter.format( *metrics )
