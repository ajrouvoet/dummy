import json
import os
import shutil
import logging

from dummy import config, git
from dummy.utils import create_dir
from dummy.models import TestResult

logger = logging.getLogger( __name__ )

RESULT_FILENAME = "result.json"

def storage_dir( commit, testname ):
	return os.path.join( config.TARGET_DIR, commit, testname )

def storage_path( commit, testname ):
	return os.path.join( storage_dir( commit, testname ), RESULT_FILENAME )

def clean_result( result ):
	""" Clean the storage dir for testresult `result`

		raises:
			OSError: When failed to remove storage dir.
	"""
	# clean the existing result dir and create a new one.
	result_dir = storage_dir( result.commit, result.test.name )
	try:
		shutil.rmtree( result_dir )
	except OSError as e:
		if not os.path.isdir( result_dir ):
			pass
		else:
			raise e

	logger.debug( "Cleaned directory: `%s`" % result_dir )

def store_result( result ):
	""" Store the completed test results to the results directory.

		raises:
			IOError: Unable to write results to disk.
	"""
	# Clean already existing results for this test.
	clean_result( result )

	# create the storage dir
	fpath = storage_path( result.commit, result.test.name )
	create_dir( fpath )

	# write the results to file
	try:
		with open( fpath, 'w' ) as fh:
			json.dump( result.serialize(), fh, sort_keys=True, indent=4 )
	except IOError as e:
		# do not write partial results
		clean_result( result )

		raise IOError( "Could not write test results to disk: %s" % str( e ))

	logger.debug( "Stored results in `%s`" % fpath )

def load_result( committish, testname ):
	""" Load test result

		raises:
			IOError: When the results files is removed while reading.

		returns:
			TestResult instance
	"""
	logger.debug( committish )
	commit = git.describe( committish )
	fpath = storage_path( commit, testname )

	try:
		with open( fpath ) as results:
			data = json.load( results )

			result = TestResult.unserialize( data )
	except IOError as e:
		# if the file did not exist, advice the user to run the test first
		if not os.path.exists( fpath ):
			raise Exception( "No test results exists yet for test `%s`" % testname )
		else:
			raise

	logger.debug( "Loaded testresult: %s (commit: %s)" % ( str( result ), commit ))

	return result
