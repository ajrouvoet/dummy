import os

from subprocess import Popen, PIPE

from dummy import config

def plugin_environ():
	env = os.environ.copy()
	env[ 'TESTS_DIR' ] = config.TESTS_DIR
	env[ 'TEMP_DIR' ] = config.TEMP_DIR

	return env

def subprocess( args, **kwargs ):
	""" call a subprocess and blocks until it ends.
		log errors on the `dummy.subprocess` logger.

		The environment is merged with the `plugin_environ()` env.

		keyword arguments:
			see subprocess.Popen
			(stderr and stdout are not used)

		return:
			stdout data
	"""
	# merge the kwargs
	kwargs[ 'env' ] = plugin_environ().update( kwargs.get( 'env', {} ) )
	kwargs[ 'stdout' ] = PIPE
	kwargs[ 'stderr' ] = PIPE

	# run the process
	process = Popen( args, **kwargs )

	return process.communicate()[0].decode( 'utf-8' )
