import logging
import sys

from dummy.viewer.formatting import ResultFormatter, Formatter
from dummy.utils import Printer

logger = logging.getLogger( __name__ )

class LatexPrinter( Printer ):

	def __init__( self, indent="\t" ):
		super( LatexPrinter, self ).__init__( indent=indent )

		self._blocks = []
		self.document = ""

	def open_block( self, *args, **options ):
		assert len( args ) > 0, "Internal Error: Need atleast one arg"

		if len( options ) > 0:
			options = "[%s]" % ",".join([ "%s=%s" % ( key, value ) for key,value in options ])
		else:
			options = ""

		self.msg( "\\begin%s%s" % ( options, "".join([ "{%s}" % arg for arg in args ])))

		self.indent()
		self._blocks.append( args[0] )

	def close_block( self ):
		assert len( self._blocks ) != 0, "Internal Error: no lateX block open."
		block = self._blocks.pop()

		self.unindent()
		self.msg( "\\end{%s}" % block )

	def msg( self, msg ):
		self.document += super( LatexPrinter, self ).msg( msg )
		self.document += "\n"

		return msg

	def esc( self, msg ):
		return msg.replace( "_", "\\_" ).replace( "{", "\\{" )

	def out( self, stream=sys.stdout ):
		stream.write( self.document )
		stream.flush()

@Formatter.register( 'latex.table' )
class LatexTableFormatter( LatexPrinter, ResultFormatter ):

	def __init__( self, *args, **kwargs ):
		ResultFormatter.__init__( self, *args, **kwargs )
		LatexPrinter.__init__( self )

		self.outfile = kwargs.get( 'outfile', sys.stdout )

	def hline( self ): self.msg( "\\hline" )

	def make_tex( self, results, *metrics ):
		# alias this for use
		_ = self.esc

		columns = metrics

		self.open_block( "table" )
		self.open_block( "tabular", "| l | %s |" % ( " | ".join([ " c " for column in columns ])))

		# column headers
		self.hline()
		self.msg(
			"%s & %s \\\\" % (
				"\\textbf{Test}",
				" & ".join([ "\\textbf{%s}" % _( m ) for m in metrics ])
			)
		)
		self.hline()

		# rows
		for result in results:
			self.msg(
				"%s & %s \\\\" % (
					"%s (%s)" % ( _( result.test.name ), _( result.commit )),
					" & ".join([ _( str( result.get_metric( m ))) for m in metrics ])
				)
			)

		# bottom line
		self.hline()

		self.close_block()
		self.close_block()

	def format_results( self, results, *metrics ):
		self.make_tex( results, *metrics )

		self.out( self.outfile )

@Formatter.register( 'latex' )
class LatexFormatter( LatexTableFormatter ):

	def format_results( self, results, *metrics ):
		self.msg( "\\documentclass[a4paper]{report}" )
		self.open_block( "document" )
		self.make_tex( results, *metrics )
		self.close_block()

		self.out( self.outfile )
