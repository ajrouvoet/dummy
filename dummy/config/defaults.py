TEMP_DIR = '.tmp' # directory for temp files
TESTS_DIR = 'tests' # directory with all the tests

SUITES = {
	'all': [ '%s/*' % TESTS_DIR ]
}

GIT_TAG_RELEASE_REGEX = r".*"
RELEASES = {}
TEST_RUNNER = '%s/bin/runner.sh'
METRICS = {}
