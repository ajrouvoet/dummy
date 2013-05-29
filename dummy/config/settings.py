""" The settings contain the specifics on how to run dummy on a project.
	
	All settings are not allowed to import any files from dummy.
"""
import os
import sys

TEMP_DIR = '.tmp'
""" Directory for temp files. """
TESTS_DIR = 'tests'
""" Directory with all the tests. """
TEST_OUTPUT_DIR = os.path.join( TEMP_DIR, 'logs' )
""" Directory to store the output logs in. """
TARGET_DIR = 'results' 
""" Store results in this directory. """
SRC_DIR = 'src'
""" The directory where the sources are stored. """
INPUT_ENCODING = 'utf8'
""" Input encoding of the terminal. """

ENV = [
	'TEMP_DIR',
	'TESTS_DIR',
	'SRC_DIR',
]
""" ENV contains the various environment variables.
"""

GIT_TAG_RELEASE_REGEX = r".*"
RELEASES = {}
TEST_RUNNER = 'bin/run.sh'

def STORAGE_DIR( test, commit ):
	""" Returns the paths to the storage directory of a test result
	"""
	return os.path.join( TARGET_DIR, commit, test.name )

# import the project settings overrides
try:
	if os.path.exists( os.path.join( os.getcwd(), 'dummy_settings.py' )):
		sys.path.append( os.getcwd() )
		from dummy_settings import *
except ImportError as e:
	pass
