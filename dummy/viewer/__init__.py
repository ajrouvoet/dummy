from dummy.viewer.formatter import ResultManager

def show( args ):
	commit = 'HEAD'
	if args.commit is not None:
		logger.debug( "Loading result from committish `%s`" % args.commit )
		commit = args.commit

	# discover the tests we need to run and add them to the runner
	_discover_tests( runner, args )
	_discover_targets( runner, args )

	for test in runner.tests:
		try:
			runner.add_result( JsonStorageProvider.load( commit, target, test ))
		except ValueError as e:
			logger.error( "No test results exists yet for test `%s`" % test.name )
			logger.debug( "Exception output: `%s`" % e )
	if args.plot:
		f = runner.plot
	else:
		f = runner.output

	if args.metric is not None:
		f( *args.metric )
	else:
		f( plot=args.plot )

def output( self, *metrics ):
	from dummy.formatter import LogFormatter

	resultmanager = ResultManager( self.results )
	resultmanager.format( *metrics, formatter=LogFormatter )

def plot( self, *metrics ):
	from dummy.formatter.plotting import PlotFormatter

	resultmanager = ResultManager( self.results )
	resultmanager.format( *metrics, formatter=PlotFormatter )
