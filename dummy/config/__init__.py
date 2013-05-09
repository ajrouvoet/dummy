import os
import sys

DUMMY_CONFIG_FILE = 'dummy_config.py'

# import the defaults
# to prevent missing values
from dummy.config.defaults import *

# import the project configuration
# if this fails we cannot proceed
try:
	# we search for it from the cwd up
	# and add the directory that contains the configuration to the path
	for ( path, dirs, files ) in os.walk( os.getcwd(), topdown=False ):
		if os.path.exists( os.path.join( path, DUMMY_CONFIG_FILE )):
			sys.path.append( path )
			break

	from dummy_config import *

except ImportError as e:
	# clearify the error a bit
	raise ImportError( "Project configuration could not be imported: %s" % e.msg )
