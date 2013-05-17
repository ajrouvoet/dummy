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
	rheader = re.compile( r'^TN:(?P<name>.*)$' )
	rfooter = re.compile( r'^end_of_record$' )
	rpath = re.compile( r'^SF:(?P<path>.*)$' )
	rfunction_hits = re.compile( r'^FNDA:(?P<hits>\d+),(?P<name>.*)$' )
	rfunctions_found= re.compile( r'^FNF:(?P<found>\d+)$' )
	rfunctions_hit = re.compile( r'^FNH:(?P<hits>\d+)$' )
	rlines_found = re.compile( r'^LF:(?P<found>\d+)$' )
	rlines_hit = re.compile( r'^LH:(?P<hits>\d+)$' )

	def parse( self, output ):
		""" Parses lcov output into a dictionary

			returns:
				{dict}: coverage results of the form:
							{
								'<filename>': {
									'lines': <int>,
									'lines_hit': <int>,
									'branches': <int>,
									'branches_hit': <int>,
									'functions': {
										'<name'>: <times_run>
										'<name'>: <times_run>
										...
									}
								}
							}
		"""
		result = {}
		fresult = None
		fpath = None

		for line in output.splitlines():
			# first make sure we are in a file section
			if fresult is None and CCoverageCollector.rheader.match( line ):
				fresult = {
					'function_coverage': {}
				}

				continue
			else:
				# single function hits
				m = CCoverageCollector.rfunction_hits.match( line )
				if m is not None:
					fresult[ 'function_coverage' ][ m.group( 'name' )] = int( m.group( 'hits' ))
					continue

				# functions hit
				m = CCoverageCollector.rfunctions_hit.match( line )
				if m is not None:
					fresult[ 'functions_hit' ] = int( m.group( 'hits' ))
					continue

				# functions found
				m = CCoverageCollector.rfunctions_found.match( line )
				if m is not None:
					fresult[ 'functions' ] = int( m.group( 'found' ))
					continue

				# lines hit
				m = CCoverageCollector.rlines_hit.match( line )
				if m is not None:
					fresult[ 'lines_hit' ] = int( m.group( 'hits' ))
					continue

				# lines found
				m = CCoverageCollector.rlines_found.match( line )
				if m is not None:
					fresult[ 'lines' ] = int( m.group( 'found' ))
					continue

				# file path
				m = CCoverageCollector.rpath.match( line )
				if m is not None:
					fpath = m.group( 'path' )
					continue

				# make sure we close the file section properly
				m = CCoverageCollector.rfooter.match( line )
				if m is not None:
					assert fpath is not None, "lcov file section had no SF entry (no file path)"
					result[ fpath ] = fresult
					fresult = None
					continue

				# if we got here, we got an unrecognized line
				logger.debug( "Got unrecognizable line: %s" % line )
		
		return result

	def pre_test_hook( self, test ):
		# zero the coverage counters
		gcov = Popen([ 'lcov', '-z', '-d', test.env().get( 'SRC_DIR' ) ])
		ret = gcov.wait()

		# make sure this was succesfull
		assert ret == 0, "Zeroing the coverage counters in the SRC_DIR failed"

	def collect( self, test ):
		result = {}

		# collect the lcov data from the src directory
		src = test.env().get( 'SRC_DIR' )

		lcov = Popen([ 'lcov', '-c', '-b', src, '-d', src ], stdout=PIPE, stderr=PIPE )
		out, err = lcov.communicate()
		out = out.decode( 'utf-8' )

		logger.debug( out )
		# if no gcda files were found lcov fails
		# but this can be a valid data
		# so report this to the user as a warning
		if lcov.returncode == 1:
			logger.warn( "lcov failed for test `%s`:\n\n%s" % ( test.name, err.decode( 'utf-8' )))

		return self.parse( out )
