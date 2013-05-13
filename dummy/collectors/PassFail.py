from dummy.collectors import Collector
from dummy.models import Test

class PassFail(Collector):
	""" A class for Pass/Fail collecting
	"""

	def __init__(self, type="value"):
		assert type in Collector.TYPE_CHOICES, "Unknown collector type: `%s`" % type
		self.type = type

	def collect(self, test):
		#mimic script
		output = 'FAIL'
		with open('test.path' + 'sim_out.txt', 'r') as sim_out:
			for line in sim_out:
				if 'PASS' in line:
					output = 'PASS'
		return self.parse_output(output)