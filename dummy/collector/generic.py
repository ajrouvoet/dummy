import os
from subprocess import Popen, PIPE
import fnmatch
import re
import logging
import json

from dummy.collector import Collector

 # don't show debug message per default
logger = logging.getLogger( __name__ )
logger.setLevel( logging.INFO ) # hide debug messages per default

class PassFailCollector( Collector ):
	""" A class for Pass/Fail collecting
	"""

	def __init__( self ):
		super( PassFailCollector, self ).__init__( type="value" )

	def collect( self, test, **kwargs ):
		# mimic script
		result = 'FAIL'
		with open( test.log_path(), 'r' ) as log:
			for line in log:
				if 'PASS' in line:
					result = 'PASS'

		return self.parse_output( result )

class CCoverageCollector( Collector ):

	blocks = re.compile( "(?:\r\n\s*\r\n|\n\s*\n)", re.MULTILINE )
	rname = re.compile( "^(?P<type>(?:Function|File)) '(?P<name>.*?)'" )
	rlines_executed = re.compile( "^Lines executed:(?P<perc>[\d.]+)% of (?P<total>[\d]+)" )
	rbranches_executed = re.compile( "^Branches executed:(?P<perc>[\d.]+)% of (?P<total>\d+)" )
	rno_branches = re.compile( "^No branches" )
	rno_calls = re.compile( "^No calls" )
	rtaken_gt_once = re.compile( "^Taken at least once:(?P<perc>[\d.]+)% of (?P<total>\d+)" )
	rcalls_executed = re.compile( "^Calls executed:(?P<perc>[\d.]+)% of (?P<total>\d+)" )

	def parse( self, output ):
		results = {
			'functions': {}
		}

		current = []
		blocks = CCoverageCollector.blocks.split( output )

		# parse the individual blocks
		for b in blocks:
			# these can be either 'Function'
			# or 'File' descriptor blocks.
			# most of blocks are function descr. so test that one first for speed opt
			m = CCoverageCollector.rname.match( b )

			# not recognized block catch
			if m is None:
				logger.debug( "Got unrecognizable block: %s" % b )
				continue

			if m.group( 'type' ) == "Function":
				results[ 'functions' ][ m.group( 'name' )] = self.parse_block( b )
			elif m.group( 'type' ) == "File":
				results[ 'file' ] = m.group( 'name' )
				results.update( self.parse_block( b ))
			else:
				logger.debug( "Got unrecognizable block: %s" % b )
				continue

		return results

	def parse_block( self, func ):
		'''
		Function 'Transition_destroy'
		Lines executed:100.00% of 3
		No branches
		No calls
		'''
		result = {}

		for line in func.splitlines():
			# skip naming lines, since they were covered in parse
			m = CCoverageCollector.rname.match( line )
			if m is not None:
				continue

			# lines executed
			m = CCoverageCollector.rlines_executed.match( line )
			if m is not None:
				result[ 'lines_executed' ] = float( m.group( 'perc' ))
				result[ 'lines' ] = float( m.group( 'total' ))
				continue

			# branches taken
			m = CCoverageCollector.rbranches_executed.match( line )
			if m is not None:
				result[ 'branches_executed' ] = float( m.group( 'perc' ))
				result[ 'branches' ] = float( m.group( 'total' ))
				continue

			# no branches
			m = CCoverageCollector.rno_branches.match( line )
			if m is not None:
				result[ 'branches_executed' ] = 0
				result[ 'branches' ] = 0
				continue

			# calls executed
			m = CCoverageCollector.rcalls_executed.match( line )
			if m is not None:
				result[ 'calls_executed' ] = float( m.group( 'perc' ))
				result[ 'calls' ] = float( m.group( 'total' ))
				continue

			# no calls
			m = CCoverageCollector.rno_calls.match( line )
			if m is not None:
				result[ 'calls_executed' ] = 0
				result[ 'calls' ] = 0
				continue

			# if we got here, we got an unrecognized line
			logger.debug( "Got unrecognizable line: %s" % line )

		return result

	def collect( self, test, env={} ):
		result = {}

		# call gcov for every source file to collect the coverage data per file
		src = env.get( 'SRC_DIR' )
		for path, dirnames, filenames in os.walk( src ):
			# filter on c files
			for fname in fnmatch.filter( filenames, '*.c' ):
				fpath = os.path.join( src, fname )

				gcov = Popen([ 'gcov', '-nfb', fpath ], stdout=PIPE, stderr=PIPE )
				out, err = gcov.communicate()
				out = out.decode( 'utf-8' )

				result[ fname ] = self.parse( out )

		return result
