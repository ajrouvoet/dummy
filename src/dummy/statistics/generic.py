import os
import glob
import logging
import datetime
from subprocess import check_call, PIPE, CalledProcessError

from dummy.statistics import Engine
from dummy import config
from dummy.runner.collectors.generic import CCoverageCollector
from dummy.utils import lcov

logger = logging.getLogger( __name__ )

class CountEngine( Engine ):

	def __init__( self, metric ):
		assert len( metric ) > 0, "CountEngine requires a metric name"
		super( CountEngine, self ).__init__( metric )

		self.bars = {
			'total': 0
		}

	def get_result( self ):
		# calculate percentages
		# yeah this is valid
		total = self.bars.get( 'total', 1 )

		self.bars = {
			key: { '#': value, '%': ( float( value )/ total ) * 100 }
			for key, value in self.bars.items()
		}

		return self.bars

	def process( self, data ):
		if self.bars.get( data ) is None:
			self.bars[ data ] = 1
		else:
			self.bars[ data ] += 1

		self.bars[ 'total' ] += 1

class KeyValueCountEngine( Engine ):

	def __init__( self, metric ):
		assert len( metric ) > 0, "KeyValueCountEngine requires a metric name"
		super( KeyValueCountEngine, self ).__init__( metric )

		self.bars = {
			'total': 0
		}

	def get_result( self ):
		return self.bars

	def process( self, data ):
		try:
			for key, value in data.items():
				self.bars[ key ] = self.bars.get( key, 0 ) + int( value )
				self.bars[ 'total' ] += int( value )
		except TypeError as e:
			logger.error( "Badly formatted rulestat result file." )
			raise

class TimerEngine( Engine ):

	def __init__( self ):
		super( TimerEngine, self ).__init__( metric=None )

		self.first = None
		self.last = None
		self.duration = datetime.timedelta( seconds=0 )

	def get_result( self ):
		return {
			'started': self.first,
			'ended': self.last,
			'duration (test runtime)': self.duration,
			'duration (ended - started)': self.last - self.first
		}

	def process( self, result ):
		if self.first is None or result.started < self.first:
			self.first = result.started

		if self.last is None or result.completed > self.last:
			self.last = result.completed

		self.duration = self.duration + ( result.completed - result.started )

class ConditionalFrequencyEngine( Engine ):
	""" Computes frequency of metric2=E output based on metric1=R value.
	"""

	def __init__( self, metric1, metric2, metric2_value, preformat=(lambda x: x) ):
		super( ConditionalFrequencyEngine, self ).__init__()
		self.metric1 = metric1
		self.metric2 = metric2
		self.metric2_value = metric2_value
		self.preformat = preformat

	def run( self, results ):
		matches={}
		totals={}
		for result in results:
			metric2_out = result.get_metric( self.metric2 )
			for item in self.preformat( result.get_metric( self.metric1 ) ):
				if metric2_out == self.metric2_value:
					matches[item] = matches.get( item, 0 ) + 1
				totals[item] = totals.get( item, 0 ) + 1

		#totals={}
		freqs={}
		for key, value in totals.items():
			freqs[key] = (matches.get( key, 0 ) * 1.0) / totals[key]
		return freqs

class CCoverageOverviewEngine( Engine ):

	def __init__( self ):
		super( CCoverageOverviewEngine, self ).__init__( metric=None )

		self.collectpath = os.path.join( config.TEMP_DIR, "coverage_collect.info" )
		self.paths = []

	def get_result( self ):
		lcov.combine( self.collectpath, paths=self.paths )

		with open( self.collectpath ) as fh:
			# parse the accumulated data
			results = lcov.parse( fh.read() )

		return results

	def process( self, result ):
		# create the path
		path = os.path.join( config.STORAGE_DIR( result.test, result.commit ),
			CCoverageCollector.FILENAME )

		# check if it exists
		if not os.path.exists( path ):
			logger.warn( "Result for test %s has no coverage data attached" % str( result ) )
		else:
			self.paths.append( path )
