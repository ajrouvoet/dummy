import re
import logging
from subprocess import Popen, PIPE, CalledProcessError, check_output as _check_output

from dummy import config
from dummy.utils import io

__all__ = ( "parse", "baseline" )
logger = logging.getLogger( __name__ )

# alias check_output to not pipe to stdout
check_output = lambda cmd: _check_output( cmd, stderr=PIPE )

class LcovError( Exception ): pass

class Parser:

	rheader = re.compile( r'^TN:(?P<name>.*)$' )
	rfooter = re.compile( r'^end_of_record$' )
	rpath = re.compile( r'^SF:(?P<path>.*)$' )
	rfunction_hits = re.compile( r'^FNDA:(?P<hits>\d+),(?P<name>.*)$' )
	rfunctions_found= re.compile( r'^FNF:(?P<found>\d+)$' )
	rfunctions_hit = re.compile( r'^FNH:(?P<hits>\d+)$' )
	rlines_found = re.compile( r'^LF:(?P<found>\d+)$' )
	rlines_hit = re.compile( r'^LH:(?P<hits>\d+)$' )

	@staticmethod
	def parse( info ):
		""" Parses lcov info file into a dictionary

			args:
				info: lcov info data to parse

			returns:
				{dict}: coverage results of the form:
							{
								'files': {
									'<filename>': {
										'lines': <int>,
										'lines_hit': <int>,
										'functions': <int>,
										'functions_hit': <int>,
										'branches': <int>,
										'branches_hit': <int>,
										'functions': {
											'<name'>: <times_run>
											'<name'>: <times_run>
											...
										}
									}
								},
								'lines': <int>,
								'lines_hit': <int>,
								'functions': <int>,
								'functions_hit': <int>
							}

			raises:
				TypeError: When the info file is not formatted correctly.
		"""
		result = {
			'files': {}
		}
		fresult = None
		fpath = None

		# totals over the test
		lines = 0
		lines_hit = 0
		functions = 0
		functions_hit = 0

		for line in info.splitlines():
			# first make sure we are in a file section
			if fresult is None:
				m = Parser.rpath.match( line )
				if m is not None:
					fresult = {
						'function_coverage': {}
					}
					fpath = m.group( 'path' )

					continue
				elif Parser.rheader.match( line ):
					continue
				else:
					raise TypeError( "Invalid coverage file format." )

				continue
			else:
				# single function hits
				m = Parser.rfunction_hits.match( line )
				if m is not None:
					fresult[ 'function_coverage' ][ m.group( 'name' )] = int( m.group( 'hits' ))
					continue

				# functions hit
				m = Parser.rfunctions_hit.match( line )
				if m is not None:
					hit = int( m.group( 'hits' ))
					fresult[ 'functions_hit' ] = hit

					# also add to the total
					functions_hit += hit

					continue

				# functions found
				m = Parser.rfunctions_found.match( line )
				if m is not None:
					found = int( m.group( 'found' ))
					fresult[ 'functions' ] = found

					# also add to the total
					functions += found

					continue

				# lines hit
				m = Parser.rlines_hit.match( line )
				if m is not None:
					hit = int( m.group( 'hits' ))
					fresult[ 'lines_hit' ] = hit

					# total
					lines_hit += hit

					continue

				# lines found
				m = Parser.rlines_found.match( line )
				if m is not None:
					found = int( m.group( 'found' ))
					fresult[ 'lines' ] = found

					# total
					lines += found

					continue

				# make sure we close the file section properly
				m = Parser.rfooter.match( line )
				if m is not None:
					assert fpath is not None, "lcov file section had no SF entry (no file path)"
					result[ 'files' ][ fpath ] = fresult
					fresult = None
					continue

				# if we got here, we got an unrecognized line
				# logger.debug( "Got unrecognizable line: %s" % line )

		result[ 'lines' ] = lines
		result[ 'lines_hit' ] = lines_hit
		result[ 'functions' ] = functions
		result[ 'functions_hit' ] = functions_hit

		return result

# alias that shit
def parse( info ): return Parser.parse( info )

def makeopts( destination=None ):
	opts = []

	# set output
	if destination is not None:
		opts += [ '-o', destination ]

	# specify we want branch coverage
	opts += [ '--rc', 'lcov_branch_coverage=1' ]
	# this does not work if gcno files are generated in another dir
	# then the obj files, which is true for setups that move obj files
	# opts += [ '--no-external' ]

	return opts

def _extract( path, extract ):
	opts = makeopts( path )

	opts += [ "--extract", path]
	for p in extract:
		opts.append( p )

	try:
		check_output([ 'lcov' ] + opts )
	except CalledProcessError as e:
		logger.debug( "Lcov reported: %s" % e.output )
		raise LcovError( "Filtering the coverage data failed" )

def _remove( path, remove ):
	opts = makeopts( path )

	# set removes
	opts += [ "--remove", path ]
	for p in remove:
		opts.append( p )

	try:
		check_output([ 'lcov' ] + opts )
	except CalledProcessError as e:
		logger.debug( "Lcov reported: %s" % e.output )
		raise LcovError( "Filtering the coverage data failed" )

def filter( path, extract=[], remove=[] ):
	if len( extract ) > 0:
		_extract( path, extract )

	if len( remove ) > 0:
		_remove( path, remove )

def baseline( destination, srcdirs, extract=[], remove=[] ):
	assert len( srcdirs ) != 0, "Need atleast one srcdir to collect coverage from"
	opts = makeopts( destination )

	# set src
	for s in srcdirs:
		opts += [ '-d', s ]

	# create the baseline
	try:
		# make sure the target dir exists
		io.create_dir( destination )

		# create the baseline
		check_output([ 'lcov', '-c', '-i' ] + opts )

		# apply file filtering
		filter( destination, extract=extract, remove=remove )
	except CalledProcessError as e:
		logger.debug( "Lcov reported: %s" % e.output )
		raise LcovError( "Setting the lcov baseline failed" )

def collect( destination, srcdirs, baseline=None, extract=[], remove=[] ):
	assert len( srcdirs ) != 0, "Need atleast one srcdir to collect coverage from"
	opts = makeopts( destination )

	# set src
	for s in srcdirs:
		opts += [ '-d', s ]

	try:
		# make sure the target dir exists
		io.create_dir( destination )

		# collect the coverage
		logger.debug([ 'lcov', '-c' ] + opts )
		check_output([ 'lcov', '-c' ] + opts )

		if baseline is not None:
			# combine the data with the baseline
			check_output([ 'lcov', '-a', baseline, '-a', destination ] + makeopts( destination ))

		# finally filter the collected data
		filter( destination, extract=extract, remove=remove )
	except CalledProcessError as e:
		logger.debug( "Lcov reported: %s" % e.output )
		raise LcovError( "Collecting coverage using lcov failed" )

def combine( destination, paths ):
	opts = makeopts( destination )

	# map paths to options for lcov
	for path in paths:
		opts += [ '-a', path ]
	logger.debug([ 'lcov' ] + opts )

	# combine the data with the accumulated set
	try:
		proc = check_output([ 'lcov' ] + opts )
	except CalledProcessError as e:
		logger.debug( "Lcov reported: %s" % e.output )
		raise LcovError( "Combining the coverage data with lcov failed" )

def zero( srcdirs ):
	opts = makeopts()

	# set src
	for s in srcdirs:
		opts += [ '-d', s ]

	try:
		check_output([ 'lcov', '-z' ] + opts )
	except CalledProcessError as e:
		logger.debug( "Lcov reported: %s" % e.output )
		raise LcovError( "Could not zero the coverage counters" )
