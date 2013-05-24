#/usr/bin/python
import sys
import argparse
import os
import logging
from colorlog import ColoredFormatter

# configure the dummy logger
root = logging.getLogger( 'dummy' )
root.setLevel( logging.DEBUG )

# configure the main application handler
ch = logging.StreamHandler()
root.addHandler( ch )

formatter = ColoredFormatter( "  %(white)s> %(log_color)s%(levelname)-8s %(reset)s%(message)s",
    datefmt=None,
    reset=True,
	log_colors={
		'DEBUG': 'white',
		'INFO':	'green',
		'WARNING': 'yellow',
		'ERROR': 'red',
		'CRITICAL': 'red'
	}
)
ch.setFormatter( formatter )

# make sure to add the dummy module directory to the path
sys.path.append(
	os.path.abspath( os.path.join( os.path.dirname( __file__ ), '../' ))
)

parser = argparse.ArgumentParser( description='Dummy test aggregation' )
sub = parser.add_subparsers()

# debug switch
parser.add_argument(
	'-D',
	'--debug',
	help="output stacktrace on error",
	action="store_true"
)

# `dummy run [-s] <name>`
runner = sub.add_parser( 'run', help="run tests" )
runner.set_defaults( func='run' )
runner.add_argument(
	'tests',
	help="names of the tests to run",
	nargs="*"
)
runner.add_argument(
	'-S',
	'--suite',
	help="names of the suites to run",
	action="append",
	default=[]
)
runner.add_argument(
	'-s',
	'--store',
	help="Store the test results",
	action="store_true"
)
runner.add_argument(
	'-c',
	'--commit',
	help="Run tests against a specific commit",
	action="store"
)

# `dummy run [-s] <name>`
show = sub.add_parser( 'show', help="results browsing" )
show.set_defaults( func='show' )
show.add_argument(
	'tests',
	help="names of the tests to inspect",
	nargs="*"
)
show.add_argument(
	'-S',
	'--suite',
	help="names of the suites to inspect",
	action="append",
	default=[]
)
show.add_argument(
	'-m',
	'--metric',
	help="Show a specific metric or multiple metrics",
	action="append",
	default=[]
)
show.add_argument(
	'-c',
	'--commit',
	help="Show results of a specific committish",
	action="store"
)
show.add_argument(
	'-p',
	'--plot',
	help="Show results in a plot",
	action="store_true"
)

if __name__ == "__main__":
	args = parser.parse_args()

	# set the logging level
	ch.setLevel( logging.DEBUG if args.debug else logging.INFO )

	# run the subprogram
	try:
		# do this here, to catch
		# errors from loading the configuration
		from dummy.runner import run, show

		if not hasattr( args, 'func' ): parser.print_help()
		elif args.func == 'run': run( args )
		elif args.func == 'show': show( args )

	except Exception as e:
		# to trace or not to trace
		if args.debug:
			raise
		else:
			logging.getLogger( 'dummy' ).error( str( e ))
