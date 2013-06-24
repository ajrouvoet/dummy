#!/usr/bin/python
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

# only use colored formatting if the stderr
# is connected to a tty
if sys.stderr.isatty():
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
else:
	formatter = logging.Formatter( "  > %(levelname)-8s %(message)s",
		datefmt=None
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

common_args = argparse.ArgumentParser( add_help=False )
common_args.add_argument(
	'tests',
	help="names of the tests to run",
	nargs="*"
)
common_args.add_argument(
	'-S',
	'--suite',
	help="names of the suites to run",
	action="append",
	default=[]
)
common_args.add_argument(
	'-x',
	'--exclude',
	help="Exclude a test to be run",
	action="append",
	default=[]
)
common_args.add_argument(
	'-t',
	'--target',
	help="Run a specific target",
	action="append",
	default=[]
)
common_args.add_argument(
	'-T',
	'--alltargets',
	help="Run all targets",
	action="store_true",
)
common_args.add_argument(
	'-c',
	'--commit',
	help="Run tests against a specific commit",
	action="store"
)

# `dummy run [-s] <name>`
runner = sub.add_parser( 'run', help="run tests", parents=[ common_args ])
runner.set_defaults( func='run' )
runner.add_argument(
	'-!',
	'--complement',
	help="Only run tests for which no results exist",
	action="store_true"
)
runner.add_argument(
	'-n',
	'--dryrun',
	help="Prevent storage of the test results",
	action="store_true"
)

stat = sub.add_parser( 'stat', help="Statistics gathering", parents=[ common_args ])
stat.set_defaults( func='stat', alltargets=False, complement=False )
stat.add_argument(
	'-m',
	'--metric',
	help="Show a specific metric or multiple metrics",
	action="append",
	default=[]
)
stat.add_argument(
	'-s',
	'--stat',
	help="Calculate the named stat",
	action="append",
	default=[]
)

show = sub.add_parser( 'show', help="results browsing", parents=[ common_args ] )
show.set_defaults( func='show', complement=False )
show.add_argument(
	'-m',
	'--metric',
	help="Show a specific metric or multiple metrics",
	action="append",
	default=[]
)
show.add_argument(
	'-p',
	'--plot',
	help="Show results in a plot (shortcut for --format=plot)",
	action="store_true"
)
show.add_argument(
	'--format',
	help="Specify the formatter for the results",
	action="store"
)

# `dummy quickstart`
# quickstart = sub.add_parser( "quickstart", help="Quickly set up dummy config")
# quickstart.set_defaults( func="quickstart" )

def main():
	args = parser.parse_args()

	# set the logging level
	ch.setLevel( logging.DEBUG if args.debug else logging.INFO )

	# run the subprogram
	try:
		# now we can load the runner and do stuff
		if not hasattr( args, 'func' ): parser.print_help()
		elif args.func == 'run':
			from dummy.runner import run
			run( args )
		elif args.func == 'show':
			from dummy.viewer import show
			show( args )
		elif args.func == 'stat':
			from dummy.viewer import stat
			stat( args )
		# elif args.func == 'quickstart': quickstart( args )

	except Exception as e:
		logging.getLogger( 'dummy' ).critical( str( e ))
		# to trace or not to trace
		if args.debug:
			raise

			# Then enter debug mode.
			# import pdb
			# pdb.post_mortem()

if __name__ == "__main__":
	main()
