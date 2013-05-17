import json
import os
import shutil
import logging

from dummy import config
from dummy.utils import create_dir
from dummy.models import TestResult

logger = logging.getLogger( __name__ )

RESULT_FILENAME = "result.json"

def storage_dir( name ):
	return os.path.join( config.TARGET_DIR, name )

def storage_path( name ):
	return os.path.join( storage_dir( name ), RESULT_FILENAME )

def clean_result( name ):
	""" Clean the storage dir for test `name`.

		raises:
			OSError: When failed to remove storage dir.
	"""
	# clean the existing result dir and create a new one.
	result_dir = storage_dir( name )
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
	clean_result( result.test.name )

	# create the storage dir
	fpath = storage_path( result.test.name )
	create_dir( fpath )

	# write the results to file
	try:
		with open( fpath, 'w' ) as fh:
			json.dump( result.serialize(), fh, sort_keys=True, indent=4 )
			logger.debug( "Created results dump: `%s`" % fpath )
	except IOError as e:
		# do not write partial results
		clean_result( result.test.name )

		raise IOError( "Could not write test results to disk: %s" % str( e ))

	logger.info( "Stored results in directory: `%s`" % config.TARGET_DIR )

def load_result( name ):
	""" Load test result

		raises:
			IOError: When the results files is removed while reading.

		returns:
			TestResult instance
	"""
	fpath = storage_path( name )

	logger.debug( fpath )
	try:
		with open( fpath ) as results:
			data = json.load( results )

			result = TestResult.unserialize( data )
	except IOError as e:
		# if the file did not exist, advice the user to run the test first
		if not os.path.exists( fpath ):
			raise Exception( "No test results exists yet for test `%s`" % name )
		else:
			raise

	logger.debug( "Loaded testresult: %s" % str( result ))

	return result
