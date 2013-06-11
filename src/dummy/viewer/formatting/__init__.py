class Formatter( object ):
	""" A Formatter outputs dictionaries in a certain format.
	"""

	def __init__( self, title ):
		self.title = title

	def format( self, d ):
		""" Format the given metrics according to Formatter implementation.
		"""
		raise NotImplementedError( "Not implemented" )

from dummy.viewer.formatting.streamformatters import *
from dummy.viewer.formatting.plotformatters import *
