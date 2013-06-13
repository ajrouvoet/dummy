import os
import sys
import re
import logging
import json
import shutil
from subprocess import check_call, Popen, PIPE, CalledProcessError

from dummy import config
from dummy.runner.collectors import Collector
from dummy.utils import lcov, io, git, kv_colon, subp

# don't show debug message per default
logger = logging.getLogger( __name__ )

class PassFailCollector( Collector ):
	""" A class for Pass/Fail collecting
	"""

	def __init__( self ):
		super( PassFailCollector, self ).__init__( type="value" )

	def collect( self, test ):
		# mimic script
		result = 'FAIL'
		with open( test.log_path(), 'r' ) as log:
			for line in log:
				if 'PASS' in line:
					result = 'PASS'

		return self.parse_output( result )

class CCoverageCollector( Collector ):

	BASELINE = os.path.join( config.TEMP_DIR, "coverage.baseline.info" )
	FILENAME = "coverage.info"

	def __init__( self, srcdir=config.SRC_DIR, filter=None ):
		self.srcdir = srcdir

		# Filter should not be an empty list.
		if filter is not None and len( filter ) == 0:
			self.filter = None
			logger.warn( "Filter is an empty list, ignoring..." )
		else:
			self.filter = filter

		# create the lcov log dir
		# and the baseline file
		io.create_dir( CCoverageCollector.BASELINE )
		lcov.baseline( CCoverageCollector.BASELINE, srcdir=self.srcdir )
		if self.filter not is None:
			lcov.filter( CCoverageCollector.BASELINE, self.filter )

	def pre_test_hook( self, test ):
		# zero the counters
		try:
			check_call([
				'lcov', '-z',
				'-d', self.srcdir
			], stdout=PIPE, stderr=PIPE )
		except CalledProcessError as e:
			logger.error( "Could not zero the coverage counters" )
			raise

	def collect( self, test ):
		try:
			# run lcov to get the test coverage file
			outfile = os.path.join( test.env()[ 'RESULTS_DIR' ], CCoverageCollector.FILENAME )
			io.create_dir( outfile )
			proc = Popen([ 'lcov', '-c',
				'-d', self.srcdir,
				'-b', self.srcdir,
				'-o', outfile,
				'--rc', 'lcov_branch_coverage=1',
			], stdout=PIPE, stderr=PIPE )

			# let's get the output
			out, err = proc.communicate()
			assert proc.returncode == 0

			# combine the data with the baseline
			proc = Popen([ 'lcov',
				'-a', CCoverageCollector.BASELINE,
				'-a', outfile,
				'-o', outfile,
				'--rc', 'lcov_branch_coverage=1',
			], stdout=PIPE, stderr=PIPE )

			out, err = proc.communicate()
			assert proc.returncode == 0

			# Then filter if necessary
			if self.filter is not None:
				lcov.filter( outfile, self.filter )

		except AssertionError:
			logger.warn(
				"lcov collect failed for test `%s`: %s" % (
					test.name, err.decode( config.INPUT_ENCODING ).strip()
				)
			)

			# the baseline is now the resulting coverage
			shutil.copyfile( CCoverageCollector.BASELINE, outfile )

		# if lcov ran correctly
		# read the output file
		with open( outfile ) as fh:
			out = fh.read()

		try:
			return lcov.parse( out )
		except TypeError as e:
			logger.warn( "Unable to parse lcov data: `%s`" % e )
			return {}


class RulestatCollector( Collector ):

	RULESTAT_RESULT_FILE = "rulestat.log"

	def __init__( self, path=None ):
		assert path is not None, "RulestatCollector needs the location of the rulestat output"

		self.statpath = path

	def pre_test_hook( self, test ):
		# remove the statfile
		# to zero the counters
		io.remove_file( self.statpath )

	def collect( self, test ):
		try:
			with open( self.statpath ) as fh:
				out = fh.read()
		except IOError as e:
			logger.warn( "No rulestat data found for test `%s`" % test.name )

			return {}

		# save the results in the test results
		path = os.path.join( test.env()[ 'RESULTS_DIR' ], RulestatCollector.RULESTAT_RESULT_FILE )
		io.create_dir( path )
		with open( path, 'w' ) as fh:
			fh.write( out )

		# parse the key value pairs into a dict
		parsed = kv_colon.parse( out )

		# interpret the values as integers
 		return { key: int( value ) for key, value in parsed.items() }

class ScriptCollector( Collector ):
	""" A class for running collector scripts.
	"""

	def __init__( self, path, type='value' ):
		super( ScriptCollector, self ).__init__( type=type )

		assert os.path.exists( path ), "Could not find the collector script: %s" % path
		assert type in Collector.TYPE_CHOICES, "Unknown collector type: `%s`" % type

		self._path = path

	@property
	def path( self ):
		return self._path

	def collect( self, test ):
		# run the collector script with working directory the test folder.
		abspath = os.path.abspath( test.path ).encode( 'string-escape' )
		try:

			output = subp.check_output(
				[ 	os.path.abspath( self.path ),
					test.name
				], test=test, cwd=abspath
			)
		except IOError as e:
			logger.error( "Script `%s` did not exit succesfully for test `%s`" % ( self.path, test.name ))
			output = None

		# parse the output
		return self.parse_output( output )
