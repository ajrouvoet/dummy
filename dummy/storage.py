import json
import os
import shutil
import logging

from dummy import config
from dummy.utils import create_dir

logger = logging.getLogger( __name__ )

JSON = 'json'
METHOD_CHOICES = ( JSON ) #Extend with .xml,.csv?

def clean():
	""" Clean the storage dir.

		raises:
			OSError: When failed to remove storage dir.
	"""
	# clean the existing result dir and create a new one.
	try:
		shutil.rmtree( config.TARGET_DIR )
	except OSError as e:
		if not os.path.isdir( config.TARGET_DIR ):
			pass
		else:
			raise e

	logger.debug( "Cleaned directory: `%s`" % config.TARGET_DIR )

def storage_dir( name ):
	return os.path.join( config.TARGET_DIR, name ) 

def store( resultslist, method='json' ):
	""" Store the completed test results to the results directory.

		raises:
			IOError: Unable to write results to disk.
	"""
	assert method in Storage.METHOD_CHOICES, "Unkown storage method:`%s`" % method

	clean()

	for testresult in resultslist:
		# create the storage dir
		dir = target_dir( testresult[ 'name' ])
		fpath = os.path.join( dir, 'results.json' )
		create_dir( fpath )

		# store the results with the specified method.
		if method == Storage.JSON:
			try:
				with open( fpath, 'w' ) as fh:
					json.dump( test.results, fh, sort_keys=True, indent=4 )
					logger.debug( "Created results dump: `%s`" % fpath )
			except IOError as e:
				# do not write partial results
				clean()

				raise IOError( "Could not write test results to disk: %s" % str( e ))

		#TODO further outputs (xml,csv)
	logger.info( "Stored results in directory: `%s`" % config.TARGET_DIR )


def load( ldir ):
	""" Load test results from a directory

		raises:
			IOError: When the results files is removed while reading.
	"""

	results = []
	( root, dirs, files ) = os.walk(ldir).next()
	#Iterate over the test folders. 
	for testname in dirs:
		testpath = os.path.join(root, testname)

		dirfiles = os.lisdir( testpath )
		#First try to find a .json results file.
		if 'results.json' in dirfiles:
			try:
				resultspath = os.path.join( testpath, 'results.json' )
				with open( resultspath ) as fresults:    
					data = json.load( fresults )
					tests.append( TestResult.unserialize( data ))
			except IOError as e:
				#Race condition?
				raise IOError( "Could not load results from: `%s`" % resultspath )

		#if 'results.xml' in dirfiles...
	
	return results