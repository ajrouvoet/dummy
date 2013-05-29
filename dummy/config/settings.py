import os
import sys

TEMP_DIR = '.tmp' # directory for temp files
TESTS_DIR = 'tests' # directory with all the tests
TEST_OUTPUT_DIR = os.path.join( TEMP_DIR, 'logs' )
TARGET_DIR = 'results' # Store results in this directory
SRC_DIR = 'src'
INPUT_ENCODING = 'utf8'

ENV = [
	'TEMP_DIR',
	'TESTS_DIR',
	'SRC_DIR',
]

GIT_TAG_RELEASE_REGEX = r".*"
RELEASES = {}
TEST_RUNNER = '%s/bin/runner.sh'

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
