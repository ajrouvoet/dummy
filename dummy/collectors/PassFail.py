from dummy.collectors import Collector

class PassFail(Collector):
	""" A class for Pass/Fail collecting
	"""

	def __init__(self, type="value"):
		assert type in Collector.TYPE_CHOICES, "Unknown collector type: `%s`" % type
		self.type = type

	def collect(self, test):
		#Code to check if tests have passed or not.
		output = 'success' #Placeholder
		return self.parse_output(output)