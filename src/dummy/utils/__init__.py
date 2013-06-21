""" The utils module contains various supportive classes, that ease repetetive tasks.
"""

class Printer( object ):

	INDENT = "    "

	def __init__( self, indent=INDENT ):
		self.indentation = 0
		self._indentstr = indent

	def indent( self, num=1 ): self.indentation += num

	def unindent( self, num=1 ):
		if self.indentation > 0:
			self.indentation -= num

	def msg( self, msg ):
		message = []

		for line in msg.splitlines():
			message.append( self.indentation * self._indentstr + line )

		return "\n".join( message )
