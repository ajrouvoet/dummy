import os
import sys
import glob

# config also contains all settings for easy of access
from dummy.config.settings import *

SUITES = {
	'all': [ '%s/*' % TESTS_DIR ]
}

METRICS = {}
STATISTICS = {}

# import the project configuration
# if this fails we cannot proceed
try:
	if os.path.exists( os.path.join( os.getcwd(), 'dummy_config.py' )):
		sys.path.append( os.getcwd() )
		from dummy_config import *
except ImportError as e:
	raise e
	# clearify the error a bit
	raise ImportError( "Project configuration could not be imported: %s" % str( e ))
