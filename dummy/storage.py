import json
import os
import shutil

class Storage:

	JSON = 'json'
	METHOD_CHOICES = ( JSON ) #Extend with .xml,.csv?

	def __init__( self, runner, method='json' )
		assert method in METHOD_CHOICES, "Unkown storage method:`%s`" % method
		self.method = method
		self.runner = runner
	
	def store( self ):
		""" Store the completed test results to the results directory.
		"""

		for test in self.runner.completed:
			#Clean the existing result dir and create a new one.
			storage_dir = test.get_target_dir()
			if os.path.isdir( storage_dir ):
				shutil.rmtree( storage_dir )
			os.makedirs( storage_dir )

			#Store the results with the specified method.
			if self.method == Storage.JSON:
				with open( storage_dir + 'results.json', 'w' ) as fh:
					json.dump(test.serialize(), fh, sort_keys=True, indent=4)

			#TODO further outputs (xml,csv)

