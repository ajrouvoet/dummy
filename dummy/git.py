import subprocess
import sys

class GitError( Exception ):
	pass

def checkout( committish, paths=[] ):
	""" Checkout a specific commit

		args:
			committish {str} git commit indicator (hash/tag/branch/etc)

		kwargs:
			files {list<str>} paths to checkout, defaults to all in repo

		raises:
			{Exception} if case the checkout failed
	"""
	try:
		subprocess.check_call(
			[ 'git', 'checkout', committish, '--' ] + paths,
			stderr=subprocess.PIPE
		)
	except subprocess.CalledProcessError as e:
		raise GitError( "Could not checkout commit `%s`: %s" % ( committish, e.output ))

def current_branch():
	""" Get the name of the current branch
	"""
	try:
		branch = subprocess.check_output(
				[ 'git', 'rev-parse', '--abbrev-ref', 'HEAD' ],
				stderr=subprocess.PIPE
			)\
			.decode( sys.getdefaultencoding() )\
			.strip()
	except subprocess.CalledProcessError as e:
		raise GitError( "Could not get current branch name: %s" % ( e.output ))

	return branch

def describe( committish='HEAD' ):
	""" Returns the short hash of the curent git HEAD
		or the tag if one is known
	"""
	hash = None

	# first try to get the tagname of this commit
	try:
		hash = subprocess.check_output(
			[ 'git', 'describe', '--exact-match', '--tags', committish ],
			stderr=subprocess.PIPE
		)
	except subprocess.CalledProcessError as e:
		pass

	# if that failed, get the hash
	if hash is None:
		try:
			hash = subprocess.check_output(
				[ 'git', 'describe', '--always', committish ],
				stderr=subprocess.STDOUT
			)
		except subprocess.CalledProcessError as e:
			raise GitError( "Failed to get description of git commit. Is this a git repo?" )
			logger.debug( "Git describe said: %s" % str( e ))

	return hash.decode( sys.getdefaultencoding() ).strip()
