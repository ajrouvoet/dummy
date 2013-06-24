import os
import sys

ROOT = os.path.dirname( __file__ )
TEST_RUNNER = 'tests/system_tests/run.sh'

ENV = {
}

SUITES = {
	'system': [
		'system_tests/pass',
		'system_tests/fail',
		'system_tests/exitcode/*',
	],
	'unit': [
		'unit_tests/models',
	]
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

UNIT_METRICS = {
	'pass/fail' : {
		'collector': 'dummy.honeypot.GrepCollector',
		'kwargs': {
			'statusses': {
				'OK': "PASS",
			}
		},
		'default' : "FAIL",
	}
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
	'unit': {
		'TEST_RUNNER': 'tests/unit_tests/run.sh',
		'METRICS': UNIT_METRICS,
	}
}
