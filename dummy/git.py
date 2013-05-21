import subprocess

def describe( committish='HEAD' ):
	""" Returns the short hash of the curent git HEAD
		or the tag if one is known
	"""
	hash = None

	# first try to get the tagname of this commit
	try:
		hash = subprocess.check_output(
			[ 'git', 'describe', '--exact-match', '--tags' ],
			stderr=subprocess.PIPE
		)
	except subprocess.CalledProcessError as e:
		pass

	# if that failed, get the hash
	if hash is None:
		try:
			hash = subprocess.check_output(
				[ 'git', 'describe', '--always' ],
				stderr=subprocess.STDOUT
			)
		except subprocess.CalledProcessError as e:
			raise Exception( "Failed to get description of git commit. Is this a git repo?" )
			logger.debug( "Git describe said: %s" % str( e ))

	return hash.decode( 'utf-8' ).strip()
