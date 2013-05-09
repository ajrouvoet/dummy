import os
import sys
import glob

DUMMY_CONFIG_FILE = 'dummy_config.py'

# import the defaults
# to prevent missing values
from dummy.config.defaults import *

# import the project configuration
# if this fails we cannot proceed
try:
	if os.path.exists( os.path.join( os.getcwd(), DUMMY_CONFIG_FILE )):
		sys.path.append( os.getcwd() )
		from dummy_config import *

except ImportError as e:
	# clearify the error a bit
	raise ImportError( "Project configuration could not be imported: %s" % e.msg )
