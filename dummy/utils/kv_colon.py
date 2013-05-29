""" Parses key-value files, e.g. (values are numeric):
	aoeu: 15
	asdf: 0
	yadda yadda : -1
    returns
	{'aoeu': 15, 'asdf': 0, 'yadda yadda': -1}
"""


def parse( info ):
	lines  = [ line for line in info.splitlines() if len( line )>0 ]
	keys   = [ line.split( ':' )[0].strip() for line in lines ]
	values = [ line.split( ':' )[1].strip() for line in lines ]
	return dict(zip(keys,values))
