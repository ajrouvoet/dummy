""" The configuration file for the test framework
	All CAPITALIZED names are settings
"""
from dummy.statistics.generic import CountEngine
from dummy.collectors.generic import CCoverageCollector, PassFailCollector

TEMP_DIR = '.tmp' # directory for temp files
TESTS_DIR = 'tests' # directory with all the tests
TEST_OUTPUT_DIR = os.path.join( TEMP_DIR, 'logs' )
SRC_DIR = 'src'

# determines which config variables are passed to the
# script environment
ENV = [
	'TEMP_DIR',
	'TESTS_DIR',
	'SRC_DIR',
]

# define the test suites
SUITES = {
	'perf': [
		'perf/*' # everyting in the directory perf
	],

	'perf-fast': [
		'test1'
		'test4'
	]
}

# regex that determines what git tags are treated as releases
# or None if this should be disabled
# per default, every tag is treated as a release
GIT_TAG_RELEASE_REGEX = r".*"

# manual selection of commit hashes as releases
RELEASES = {
	'beta': '5c67ae07921da8716df2ef4da40fb458c1690ee5'
}

# this is test runner executable; it takes one argument: the path to the test
TEST_RUNNER = 'bin/runner.sh'

# here you configure the metrics you would like to collect
# from the test results, how to collect them and were to store them
METRICS = {
	'cycles': {
		# the collector can be an external executable that is called
		# with the path to the test results directory as a first parameter
		'collector': 'bin/cycles.sh'
	},

	# passing/failing of a test is also configured as a collector
	'pass/fail': {
		'collector': PassFailCollector()
	},

	'coverage': {
		'collector': CCoverageCollector,

		# we expect the collector script it to print the value
		# of the measured metric to the STDOUT stream
		# STDERR is caught and reported to the user
		# the type defaults to 'value', but can be set to 'json' to have the metric parsed
		# as json before storing it
		'type': 'json',

		# additionally the script can log data to files
		# and have them copied to the test results directory
		# in this case we want to collect all .gcov files from the TEMP dir and
		# copy them to the coverage directory in the test results dir
		'files': [
			{
				'src': '%s/coverage/*.gcov' % TEMP,
				'dest': '%s/coverage/' % TEMP
			}
		]
	}
}

# custom statistics function
def function_cov( stat, coverage ):
	# loop over the function coverage
	# information and add one to the statistic for every function that is
	# at least partially covered
	for f in coverage.functions:
		if f.coverage > 0:
			state += 1

STATISTICS = {
	# we can configure what statistics are gathered over the different tests
	# several statistics engines exist in the python module `dummy.statistics.generic`

	# let's count for example the amount of tests failed/passed
	'tests passing': {
		'engine': CountEngine
	}
}
