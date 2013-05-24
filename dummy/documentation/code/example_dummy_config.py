import os
from dummy.collectors.generic import PassFailCollector
from dummy.statistics.generic import CountEngine

TEMP_DIR = '.tmp' # directory for temp files
TESTS_DIR = 'tests' # directory with all the tests
TEST_OUTPUT_DIR = os.path.join( TEMP_DIR, 'logs' )
TARGET_DIR = 'results' # Store results in this directory
SRC_DIR = 'src'

ENV = [
	'TEMP_DIR',
	'TESTS_DIR',
	'SRC_DIR',
]

SUITES = {
	'all': [ '%s/*' % TESTS_DIR ]
}

GIT_TAG_RELEASE_REGEX = r".*"
RELEASES = {}
TEST_RUNNER = '%s/bin/runner.sh'
METRICS = {
        # passing/failing of a test is configured as a collector
        'pass/fail': {
                'collector': PassFailCollector()
        },
}
STATISTICS = {
        # we can configure what statistics are gathered over the different tests
        # several statistics engines exist in the python module `dummy.statistics.generic`

        # let's count for example the amount of tests failed/passed
        'tests passing': {
                'engine': CountEngine
        },
}
