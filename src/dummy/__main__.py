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

class CommonArguments( argparse.ArgumentParser ):
	"""Arguments common to all dummy options.
	"""
	def __init__( self, **kwargs ):
		kwargs['add_help'] = False
		super( CommonArguments, self ).__init__( **kwargs )
		
		self.add_argument(
			'tests',
			help="names of the tests to run",
			nargs="*"
		)
		self.add_argument(
			'-S',
			'--suite',
			help="names of the suites to run",
			action="append",
			default=[]
		)
		self.add_argument(
			'-x',
			'--exclude',
			help="Exclude a test to be run",
			action="append",
			default=[]
		)
		self.add_argument(
			'-t',
			'--target',
			help="Run a specific target",
			action="append",
			default=[]
		)
		self.add_argument(
			'-T',
			'--alltargets',
			help="Run all targets",
			action="store_true",
		)
		self.add_argument(
			'-c',
			'--commit',
			help="Run tests against a specific commit",
			action="store"
		)

class DummyArgparser( argparse.ArgumentParser ):
	@classmethod
	def build( cls, **kwargs ):
		""" Build a Dummy Argparser.

			Builder pattern is used to prevent endless recursion.

			:returns argparse.ArgumentParser: configured for dummy.
		"""
		kwargs[ 'description' ] = "Dummy test aggregation"
		parser = cls( **kwargs )
		# debug switch
		parser.add_argument(
			'-D',
			'--debug',
			help="output stacktrace on error",
			action="store_true"
		)
		
		# Add subcommands
		commands = parser.add_subparsers( help = "Dummy commands" )
		parser.add_run( commands )
		parser.add_stat( commands )
		parser.add_show( commands )

		return parser
		
	def add_run( self, subparser ):
		""" Add the run command to subparser.
		"""
		runner = subparser.add_parser( 'run', help="run tests", parents=[ CommonArguments() ])
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

	def add_stat( self, subparser ):
		""" Add the stat command to subparser.
		"""
		stat = subparser.add_parser( 'stat', help="Statistics gathering", parents=[ CommonArguments() ])
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
			help="Calculate the named stats",
			action="append",
			default=[]
		)


	def add_show( self, subparser ):
		""" Add the show command to subparser.
		"""
		show = subparser.add_parser( 'show', help="results browsing", parents=[ CommonArguments() ] )
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
			help="Specify the formatter for the results [default is log]",
			action="store",
			default="log"
		)

def main():
	parser = DummyArgparser.build()
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
