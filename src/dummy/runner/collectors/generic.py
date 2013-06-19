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

class LogCollector( Collector ):

	FILENAME = "run.log"

	def collect( self, test ):
		# output file
		outfile = os.path.join( test.env()[ 'RESULTS_DIR' ], LogCollector.FILENAME )
		io.create_dir( outfile )

		try:
			shutil.copy( test.log_path(), outfile )
		except IOError as e:
			logger.error( "Failed to copy the log file to the test results" )
			logger.debug( "OS reported: %s" % str( e ))

		return None

class GrepCollector( Collector ):

	def __init__( self, statusses, default=None ):
		super( GrepCollector, self ).__init__( type="value" )

		self.statusses = statusses
		self.default = default

	def collect( self, test ):
		# try to grep one of the status greps
		with open( test.log_path(), 'r' ) as log:
			for line in log:
				for grep, status in self.statusses.items():
					if grep in line: return status

		return self.default

class PassFailCollector( GrepCollector ):
	""" A class for Pass/Fail collecting
	"""

	def __init__( self ):
		super( PassFailCollector, self ).__init__({
			'PASS':	'PASS'
		}, default="FAIL" )

class CCoverageCollector( Collector ):

	BASELINE = os.path.join( config.TEMP_DIR, "coverage.baseline.info" )
	FILENAME = "coverage.info"

	def __init__( self, srcdirs=[ config.SRC_DIR ], extract=[], remove=[] ):
		self.srcdirs = srcdirs
		self.extract = extract
		self.remove = remove

		# create the coverage baseline
		lcov.baseline(
			CCoverageCollector.BASELINE,
			srcdirs=self.srcdirs,
			extract=self.extract,
			remove=self.remove
		)

	def pre_test_hook( self, test ):
		# zero the counters
		lcov.zero( srcdirs=self.srcdirs )

	def collect( self, test ):
		# run lcov to get the test coverage file
		outfile = os.path.join( test.env()[ 'RESULTS_DIR' ], CCoverageCollector.FILENAME )

		# create the coverage
		try:
			lcov.collect( outfile, self.srcdirs, CCoverageCollector.BASELINE,
				extract=self.extract,
				remove=self.remove
			)
		except lcov.LcovError as e:
			logger.warn(
				"Lcov collection failed: `%s`" % e
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
