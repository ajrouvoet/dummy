import os
import sys
import logging
import subprocess as subp

from dummy.config import settings
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

	for name in settings.ENV:
		env[ name ] = getattr( settings, name )

	if test is not None:
		env[ 'TEST_NAME' ] = test.name
		env[ 'TEST_LOG' ] = test.log_path()
		env[ 'RESULTS_DIR' ] = os.path.join(
			settings.TEMP_DIR,
			settings.STORAGE_DIR( test, commit=git.describe() )
		)

	return env

def subprocess( args, test=None, **kwargs ):
	""" call a subprocess and blocks until it ends, returning the decode data of stdout.
		stderr is redirected to stdout as well.

		The environment is merged with the `plugin_environ()` env.

		:param kwargs:
			see subprocess.Popen for kwargs (except stderr and stdout)

			test: test instance; used to set a proper env.

		:return:
			stdout data

		:raises:
			CalledProcessError: When the process exits with a non-zero exit code.
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
		return stdout.decode( settings.INPUT_ENCODING )
	except OSError as e:
		if type( args[0] ) == 'list':
			proc = " ".join( args[0] )
		else:
			proc = args[0]

		raise OSError( "Failed to execute `%s`. OS said: %s" % ( proc, str( e )))
	except CalledProcessError as e:
		logger.debug( "Process output: `%s`" % stdout.decode( settings.INPUT_ENCODING ))
		raise CalledProcessError( "The process exited with a non-zero exit code." )

