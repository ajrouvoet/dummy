import os
import sys
import re
import logging
import json
import shutil
from subprocess import check_call, Popen, PIPE, CalledProcessError

from dummy import config
from dummy.collector import Collector
from dummy.utils import lcov, io, git, kv_colon

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

	def pre_test_hook( self, test ):
		# zero the counters
		try:
			check_call([
				'lcov', '-z',
				'-d', test.env().get( 'SRC_DIR' )
			], stdout=PIPE, stderr=PIPE )
		except CalledProcessError as e:
			logger.error( "Could not zero the coverage counters" )
			raise

		# create the lcov log dir
		# and the baseline file
		io.create_dir( CCoverageCollector.BASELINE )
		lcov.baseline( CCoverageCollector.BASELINE )

	def collect( self, test ):
		# collect the lcov data from the src directory
		src = test.env().get( 'SRC_DIR' )

		try:
			# run lcov to get the test coverage file
			outfile = os.path.join( test.env().get( 'RESULTS_DIR' ), CCoverageCollector.FILENAME )
			io.create_dir( outfile )
			proc = Popen([ 'lcov', '-c',
				'-d', src,
				'-b', src,
				'-o', outfile
			], stdout=PIPE, stderr=PIPE )

			# let's get the output
			out, err = proc.communicate()
			assert proc.returncode == 0

			# combine the data with the baseline
			proc = Popen([ 'lcov',
				'-a', CCoverageCollector.BASELINE,
				'-a', outfile,
				'-o', outfile
			], stdout=PIPE, stderr=PIPE )

			out, err = proc.communicate()
			assert proc.returncode == 0
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

		return lcov.parse( out )

class RulestatCollector( Collector ):

	FILENAME = "rulestat_out.txt"

	def pre_test_hook( self, test ):
		# zero the counters
		# and the baseline file
		srcdir = test.path
		results_file = os.path.join( srcdir, self.FILENAME)


	def collect( self, test ):
		# collect the lcov data from the src directory
		srcdir = test.path
		results_file = os.path.join( srcdir, self.FILENAME)

		with open( results_file ) as fh:
			out = fh.read()

		return kv_colon.parse( out )
