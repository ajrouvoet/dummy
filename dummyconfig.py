import os
import sys

ROOT = os.path.dirname( __file__ )
TEST_RUNNER = 'tests/run.sh'

ENV = {
}

SUITES = {
	'all': [
		'pass',
		'fail',
		'exitcode/*',
	],
}

METRICS = {
	'pass/fail' : {
		'collector': 'dummy.honeypot.PassFailCollector'
	},

	'status' : {
		'collector': 'dummy.honeypot.GrepCollector',
		'kwargs': {
			'statusses': {
				'Fatal': "FATAL"
			},
			'default': None
		}
	},
}

STATISTICS = {
	'passing': {
		'engine': 'dummy.honeypot.CountEngine',
		'kwargs': {
			'metric': 'pass/fail'
		}
	},
}

TARGETS = {
}
