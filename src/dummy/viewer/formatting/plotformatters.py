from dummy.viewer.formatting import Formatter

try:
	import pylab
except ImportError as e:
	raise ImportError(
		"`matplotlib` is not installed on this system which is required for plotting results, sorry!"
	)

class PlotFormatter( Formatter ):

	def format( self, *metrics ):
		# create the figure
		fig = pylab.figure( facecolor='white' )

		# get the xlabels
		x = range( 1, len( self.testresults ) + 1 )
		xlabels = [ t.test.name for t in self.testresults ]

		pylab.title( 'Metric values per test (commit: %s)' % self.testresults[0].commit, fontsize=22 )
		pylab.xticks( rotation=20 )
		pylab.grid( True, markevery='integer' )
		pylab.xlabel( 'tests', fontsize=16 )
		pylab.margins( 0.05 )
		pylab.xticks( x, xlabels )

		# create the plots
		for metric in metrics:
			self.format_metric( metric )

		# and show it
		pylab.legend()
		pylab.show()

	def format_metric( self, metric ):
		x = range( 1, len( self.testresults ) + 1 )
		y = [ t.get_metric( metric ) for t in self.testresults ]

		try:
			plot = pylab.plot( x, y )
			pylab.setp( plot,
				label=metric,
				linestyle='dashed',
				linewidth=1.0,
				marker=".",
				markersize=12.0,
				aa=True
			)
		except TypeError as e:
			raise Exception(
				"The metric `%s` is not numeric and can thus not be plotted." % metric
			)


