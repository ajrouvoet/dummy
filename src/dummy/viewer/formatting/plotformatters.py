from dummy.viewer.formatting import ResultFormatter, Formatter
import logging

logger = logging.getLogger( __name__ )

try:
	import pylab
	import numpy

	@Formatter.register( 'plot' )
	class PlotFormatter( ResultFormatter ):

		def __init__( self, *args, **kwargs ):
			super( PlotFormatter, self ).__init__( self, *args, **kwargs )

			# create the figure
			self.figure = pylab.figure( facecolor='white' )

		def format_results( self, results, *metrics ):
			assert len( results ) > 0, "No results to format"

			self.setup( results )

			try:
				self.plot( results, metrics )
			except ( ValueError, TypeError ) as e:
				raise Exception(
					"Non numeric metrics cannot be plotted"
				)

		def setup( self, results ):
			# get the xlabels
			x = range( 1, len( results ) + 1 )
			xlabels = [ r.test.name for r in results ]

			pylab.title( 'Metric values per test (commit: %s)' % results[0].commit, fontsize=22 )
			pylab.xticks( rotation=90 )
			pylab.grid( True, markevery='integer' )
			pylab.xlabel( 'tests', fontsize=16 )
			pylab.margins( 0.05 )
			pylab.xticks( x, xlabels )

		def plot( self, results, metrics, **opts ):
			# create the plots
			plots = []
			for metric in metrics:
				plots.append( self.plot_metric( results, metric , **opts ))

			# legendary
			pylab.legend([ p[0] for p in plots], metrics )

			# and show it
			pylab.show()

		def plot_metric( self, results, metric, **opts ):
			x = range( 1, len( results ) + 1 )
			y = [ t.get_metric( metric ) for t in results ]

			try:
				plot = pylab.plot( x, y, **opts )
				pylab.setp( plot,
					label=metric,
					linestyle='dashed',
					linewidth=1.0,
					marker=".",
					markersize=12.0,
					aa=True
				)

				return plot
			except ( ValueError, TypeError ) as e:
				raise Exception(
					"The metric `%s` is not numeric and can thus not be plotted." % metric
				)

	@Formatter.register( 'plot.bar' )
	class BarPlotFormatter( PlotFormatter ):

		def plot( self, results, metrics, **opts ):
			# create the plots
			plots = []
			x = numpy.arange( len( results ))
			margin = 0.2 / len( metrics )
			width = 0.8 / len( metrics )
			colors = [
				( i/( 2 * len( metrics )), i/len(metrics), 0.8 )
				for i in range( 1, len( metrics ) + 1)
			]

			for i, metric in enumerate( metrics ):
				# compute the bar heights
				y = [ t.get_metric( metric ) or 0 for t in results ]

				plot = self.bar(
					x + 0.5 + i*width + ( i ) * margin,
					y,
					width=width,
					color=colors[i],
				)
				plots.append( plot )

				pylab.setp( plot,
					label=metric,
					aa=True
				)

			# legendary
			pylab.legend([ p[0] for p in plots], metrics )

			# and show it
			pylab.show()

		def bar( self, *args, **kwargs ):
			return pylab.bar( *args, **kwargs )

except ImportError:
	logger.debug( "matplotlib is not installed, PlotFormatter not available." )
