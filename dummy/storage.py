import json
import os
import shutil
import logging

from dummy import config
from dummy.utils import create_dir

logger = logging.getLogger( __name__ )

class Storage:

	JSON = 'json'
	METHOD_CHOICES = ( JSON ) #Extend with .xml,.csv?

	def __init__( self, runner, method='json' ):
		assert method in Storage.METHOD_CHOICES, "Unkown storage method:`%s`" % method
		
		self.method = method
		self.runner = runner

	def clean( self ):
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

	def store( self ):
		""" Store the completed test results to the results directory.

			raises:
				IOError: Unable to write results to disk.
		"""
		self.clean()

		for test in self.runner.completed:
			# create the storage dir
			dir = test.storage_dir()
			fpath = os.path.join( dir, 'results.json' )
			create_dir( fpath )

			# store the results with the specified method.
			if self.method == Storage.JSON:
				try:
					with open( fpath, 'w' ) as fh:
						json.dump( test.serialize(), fh, sort_keys=True, indent=4 )
						logger.debug( "Created results dump: `%s`" % fpath )
				except IOError as e:
					# do not write partial results
					# self.clean()

					raise IOError( "Could not write test results to disk: %s" % str( e ))

			#TODO further outputs (xml,csv)
		logger.info( "Stored results in directory: `%s`" % config.TARGET_DIR )


	def load( self, ldir ):
		""" Load test results from a directory
		"""

		tests = []
		( root, dirs, files ) = os.walk(ldir).next()[1]
		#Iterate over the test folders. 
		for testname in dirs:
			testpath = os.path.join(root, testname)

			if self.method == Storage.JSON:
				resultspath = os.path.join( testpath, 'results.json' )
			try:
				with open( resultspath ) as fresults:    
					data = json.load( fresults )
					tests.append( Test.unserialize( data ))
			except IOError as e:
				logger.info( "Could not load results from: `%s`" % resultspath )
				pass
				
