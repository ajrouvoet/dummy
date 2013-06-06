import os
import sys
import logging
import subprocess as subp

from dummy import config
from dummy.utils import git

logger = logging.getLogger( __name__ )

def plugin_environ( test=None ):
	""" extend a copy of os.environ with some testing environ vars.
		these include the config.ENV names.

		kwargs:
			test {Test}:
				for setting optional test specific variables
				(TEST_NAME, TEST_LOG)

		return:
			environment {dict}
	"""
	env = os.environ.copy()

	env[ 'TEMP_DIR' ] = config.TEMP_DIR
	env[ 'TESTS_DIR' ] = config.TESTS_DIR
	env[ 'SRC_DIR' ] = config.SRC_DIR

	for key, value in config.ENV.items():
		env[ key ] = str( value )

	if test is not None:
		env[ 'TEST_NAME' ] = test.name
		env[ 'TEST_LOG' ] = test.log_path()
		env[ 'RESULTS_DIR' ] = os.path.join(
			config.TEMP_DIR,
			config.STORAGE_DIR( test, commit=git.describe() )
		)

	return env

def subprocess( args, test=None, **kwargs ):
	""" call a subprocess and blocks until it ends, returning the decode data of stdout.
		stderr is redirected to stdout as well.

		The environment is merged with the `plugin_environ()` env.

		kwargs:
			see subprocess.Popen for kwargs (except stderr and stdout)

			test: test instance; used to set a proper env.

		return:
			stdout data
	"""
	# merge the environments
	env = plugin_environ( test=test )
	env.update( kwargs.get( 'env', {} ) )

	# setup the popen kwargs
	kwargs[ 'env' ] = env
	kwargs[ 'stdout' ] = subp.PIPE
	kwargs[ 'stderr' ] = subp.STDOUT

	# run the process
	try:
		process = subp.Popen( args, **kwargs )
	except OSError as e:
		if type( args[0] ) == 'list':
			proc = " ".join( args[0] )
		else:
			proc = args[0]

		raise OSError( "Failed to execute `%s`. OS said: %s" % ( proc, str( e )))

	return process.communicate()[0].decode( config.INPUT_ENCODING )

def check_output( args, test=None, **kwargs ):
	""" call a subprocess and blocks until it ends, returning the decode data of stdout.
		stderr is redirected to stdout as well.

		The environment is merged with the `plugin_environ()` env.

		:param kwargs:
			see subprocess.Popen for kwargs (except stderr and stdout)

			test: test instance; used to set a proper env.

		:return:
			stdout data

		:raises:
			IOError: When the process exits with a non-zero exit code.
	"""
	# merge the environments
	env = plugin_environ( test=test )
	env.update( kwargs.get( 'env', {} ) )

	# setup the popen kwargs
	kwargs[ 'env' ] = env
	#kwargs[ 'stdout' ] = subp.PIPE
	kwargs[ 'stderr' ] = subp.STDOUT

	# run the process
	try:
		stdout = subp.check_output( args, **kwargs )
		return stdout.decode( config.INPUT_ENCODING )
	except OSError as e:
		if type( args[0] ) == 'list':
			proc = " ".join( args[0] )
		else:
			proc = args[0]

		raise OSError( "Failed to execute `%s`. OS said: %s" % ( proc, str( e )))
	except subp.CalledProcessError as e:
		logger.debug( "Error output: `%s`" % e)
		raise IOError( "The process `%s` exited with a non-zero exit code." % args )
