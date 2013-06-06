import shutil
import logging
import imp

logger = logging.getLogger( __name__ )

def quickstart( args ):
	logger.info( "Welcome to Dummy quickstart, where we configure your dummy_config.py" )
	logger.info( "Are you sure you wish to continue?" )
	choice = raw_input( "[y/n]" )
	if choice != "y":
		logger.warning( "Aborting..." )

	logger.info( "Copying default configuration to current directory." )
	(file, default_path, description) = imp.find_module( dummy.config.defaults )
	shutil.copy( default_path, 'dummy_config.py' )
