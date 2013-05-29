""" The config contain the specifics on how to run dummy on a project.

	The configs can import from dummy.
"""
import os
import sys
import glob

# config also contains all settings for easy of access
from dummy.config.settings import *

SUITES = {
	'all': [ '%s/*' % TESTS_DIR ],
}
""" Contains the defined suites for this project.

	A suite contains a list of tests. Also supports wildcards globbing (e.g. `path/*`).
"""

METRICS = {}
""" Contains the metrics configured for this project.

	A metric collects information about a test result.
	See the glossary entry :term:`metric` for a definition.
"""

STATISTICS = {}
""" Contains the statistics configured for this project.

	A statistic collects aggregated information about results from all tests.
	See the glossary entry :term:`statistic` for a definition.
"""

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
