import logging

logger = logging.getLogger( __name__ )

class Statistic( object ):

	@classmethod
	def parse( cls, name, conf ):
		""" Parse a Statistic instance from a statistic configuration dictionary

			return:
				Metric instance
		"""
		engine = conf.get( 'engine' )

		assert engine is not None, "Statistic `%s` has no engine attached" % name

		return cls( name, engine )

	def __init__( self, name, engine ):
		assert len( name ) > 0, "A statistics engine must be named"

		self.name = name
		self.engine = engine

	def gather( self, results ):
		""" Collect the statistics results given a set of results
			to consider

			params:
				results {list<TestResult>}: lists of result to calculate the statistic of

			returns:
				value {any}: calculated statistic
		"""
		result = None
		try:
			result = self.engine.run( results )
		except Exception as e:
			raise Exception( "The statistics engine	`%s` did not exit succesfully: %s" %\
				( self.name, str( e ))
			)

		return result

class Engine( object ):

	def __init__( self, metric="" ):
		self.metric = metric

	def run( self, results ):
		for result in results:
			self.process( result.get_metric( self.metric ))

		return self.get_result()

	def get_result( self ):
		raise NotImplementedError( "Engine.get_result() is an abstract method" )

	def process( self, value ):
		raise NotImplementedError( "Engine.process( value ) is an abstract method" )
