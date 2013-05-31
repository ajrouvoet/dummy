import logging

logger = logging.getLogger( __name__ )

class Statistic( object ):
	""" A :term:`statistic` collects aggregated information about multiple test results.

		The statistic object uses a :class:`Engine` to collect the specified data.
	"""

	@classmethod
	def parse( cls, name, conf ):
		""" Parse a Statistic instance from a statistic configuration dictionary

			return:
				Statistic instance
		"""
		enginename = conf.get( 'engine' )
		kwargs = conf.get( 'kwargs', {} )
		args = conf.get( 'args', [] )

		assert enginename is not None, "Statistic `%s` has no engine attached" % name

		# try to import the engine
		try:
			mod, clsname = enginename.rsplit( '.', 1 )
			mod = __import__( mod, fromlist=[ clsname ] )
			engine = getattr( mod, clsname )
		except ImportError as e:
			logger.error( "Could not import the statistics engine `%s`" % enginename )
			raise e

		# try to initiate the engine
		try:
			engine = engine( *args, **kwargs )
		except TypeError:
			logger.error( "Could not initiate the statistics engine `%s`" % enginename )
			raise e

		return cls( name, engine )

	def __init__( self, name, engine ):
		assert len( name ) > 0, "A statistics engine must be named"

		self.name = name
		self.engine = engine

	def gather( self, results ):
		""" Collect the statistics results given a set of results
			to consider

			:param results: {list<TestResult>} lists of result to calculate the statistic of.

			:returns: The calculated statistic.
			:rtype: A value or dict object.
		"""
		result = None
		try:
			result = self.engine.run( results )
		except Exception as e:
			logger.error( "The statistics engine `%s` did not exit succesfully: %s" %\
				( self.name, str( e ))
			)
			raise

		return result

class Engine( object ):
	""" An engine implements the requested statistic functionality.
	"""

	def __init__( self, metric=None ):
		self.metric = metric

	def run( self, results ):
		""" Run the engine.

			:returns: The collected statistic results.
		"""
		for result in results:
			if self.metric is not None:
				self.process( result.get_metric( self.metric ))
			else:
				self.process( result )

		return self.get_result()

	def get_result( self ):
		raise NotImplementedError( "Engine.get_result() is an abstract method" )

	def process( self, value ):
		raise NotImplementedError( "Engine.process( value ) is an abstract method" )
