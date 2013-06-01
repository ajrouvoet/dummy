import json
import os
import shutil
import logging

from dummy import config
from dummy.utils import io, git
from dummy.models import TestResult

logger = logging.getLogger( __name__ )

class StorageProvider:

	def __init__( self, result ):
		self.result = result

	def clean( self ):
		# clean the existing result dir and create a new one.
		result_dir = config.STORAGE_DIR( self.result.test, commit=self.result.commit )
		try:
			shutil.rmtree( result_dir )
		except OSError as e:
			if not os.path.isdir( result_dir ):
				pass
			else:
				raise e

		logger.debug( "Cleaned directory: `%s`" % result_dir )

	def path( self ):
		""" Returns path to the result file.
		"""
		raise NotImplementedError()

	def store( self ):
		raise NotImplementedError()

class JsonStorageProvider( StorageProvider ):

	@staticmethod
	def load( commit, target, test ):
		""" Load test result

			raises:
				IOError: When the results files is removed while reading.

			returns:
				TestResult instance
		"""
		commit = git.describe( commit )
		fpath = os.path.join(
			config.STORAGE_DIR( test, commit=commit ),
			'result.json'
		)

		try:
			with open( fpath ) as results:
				data = json.load( results )

				result = TestResult.unserialize( test, data )
				result.test = test
		except IOError as e:
			# if the file did not exist, advice the user to run the test first
			if not os.path.exists( fpath ):
				raise ValueError( str( e ))
			else:
				raise

		logger.debug( "Loaded testresult: %s (commit: %s)" % ( str( result ), commit ))

		return result

	def path( self ):
		return os.path.join(
			config.STORAGE_DIR( self.result.test, commit=self.result.commit ),
			'result.json'
		)

	def store( self ):
		""" Store the completed test results to the results directory.

			raises:
				IOError: Unable to write results to disk.
		"""
		# Clean already existing results for this test.
		self.clean()

		# create the storage dir
		fpath = self.path()
		io.create_dir( fpath )

		# write the results to file
		try:
			with open( fpath, 'w' ) as fh:
				# encoding defaults to utf8; done
				json.dump( self.result.serialize(), fh, sort_keys=True, indent=4 )
		except IOError as e:
			# do not write partial results
			self.clean()

			raise IOError( "Could not write test results to disk: %s" % str( e ))

		logger.debug( "Stored results in `%s`" % fpath )
