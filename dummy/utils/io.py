import os
import os.path

import logging

logger = logging.getLogger( __name__ )

def remove_file( fpath ):
	""" deletes file if it exists

		raises:
			OSError on failure to remove the file
	"""

	try:
		if os.path.isfile( fpath ):
			os.remove( fpath )
	except OSError as e:
		if os.access( fpath, os.F_OK ): #file still exists, something's gone wrong
			raise e

def create_dir( fpath ):
	""" create the dirname of fpath if it does not exist

		raises:
			OSError on failure to create the directory and it does not exist
	"""
	path = os.path.dirname( fpath )

	try:
		os.makedirs( path )
	except OSError as e:
		if os.path.isdir( path ):
			pass
		else:
			raise e
