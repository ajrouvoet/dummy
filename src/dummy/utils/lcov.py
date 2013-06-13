import re
import logging
from subprocess import Popen, PIPE, CalledProcessError

from dummy import config

__all__ = ( "parse", "baseline" )
logger = logging.getLogger( __name__ )

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

def baseline( path, srcdir=config.SRC_DIR ):
	# create the baseline
	gcov = Popen(
		[ 	'lcov', '-c', '-i',
			'-d', srcdir,
			'-o', path,
			'--rc', 'lcov_branch_coverage=1',
		], stdout=PIPE, stderr=PIPE )
	ret = gcov.wait()
	( out, err ) = gcov.communicate()

	# make sure this was succesfull
	# or else print the error
	assert ret == 0, "Setting the lcov baseline failed"
