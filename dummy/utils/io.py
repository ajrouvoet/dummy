import os

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
