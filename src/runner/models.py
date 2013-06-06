import logging
from dummy.runner.collectors import Collector
from dummy.runner.collectors.generic import ScriptCollector

logger = logging.getLogger( __name__ )

class Metric:

	@classmethod
	def parse( cls, name, conf ):
		""" Parse a metric instance from a metric configuration dictionary

			return:
				Metric instance
		"""
		collname = conf.get( 'collector' )
		script = conf.get( 'script' )
		output_type = conf.get( 'type', Collector.VALUE )

		assert collname is not None or script is not None,\
			"Metric `%s` neither has a collector, nor a script" % name

		if collname is not None:
			kwargs = conf.get( 'kwargs', {} )
			args = conf.get( 'args', [] )

			# try to import the collector
			try:
				mod, clsname = collname.rsplit( '.', 1 )
				logger.debug( collname )
				logger.debug( mod )
				logger.debug( clsname )
				mod = __import__( mod, fromlist=[ clsname ] )
				coll = getattr( mod, clsname )
			except ImportError as e:
				logger.error( "Could not import the collector `%s`" % collname )
				raise e

			# try to initiate the collector
			try:
				coll = coll( *args, **kwargs )
			except TypeError:
				logger.error( "Could not instantiate the collector `%s`" % collname )
				raise e
		else:
			coll = ScriptCollector( script, type=output_type )

		return cls( name, collector=coll )

	def __init__( self, name, collector ):
		assert len( name ) > 0, "A metric must be named"
		assert isinstance( collector, Collector ), \
			"Metric constructor collector must be of type Collector"

		self.name = name
		self.collector = collector

	def pre_test_hook( self, test ):
		self.collector.pre_test_hook( test )

	def collect( self, test ):
		return self.collector.collect( test )

