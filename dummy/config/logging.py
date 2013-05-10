import logging

# loggers are retrieved via the logging.getLogger
# so we don't import them into the configuration
__all__ = ( 'DEBUG', )

DEBUG = True

# configure the dummy logger
root = logging.getLogger( 'dummy' )
root.setLevel( logging.DEBUG )

# configure the main application handler
ch = logging.StreamHandler()
ch.setLevel( logging.DEBUG if DEBUG else logging.INFO )

formatter = logging.Formatter( "  >> %(name)s (%(levelname)s):\t%(message)s" )
ch.setFormatter( formatter )

root.addHandler( ch )
