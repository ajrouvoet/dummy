import unittest
import sys, os

sys.path.append( os.path.abspath( os.path.join( os.path.dirname( __file__ ),'..','..','..','src' )))

from dummy.models import TestResult
from datetime import datetime

class MicroMock(object):
	def __init__(self, **kwargs):
		self.__dict__.update(kwargs)

TEST_MOCK = MicroMock( name = "TestName" )
START_TIME = datetime.now()
STOP_TIME = datetime.now()
TARGET = "Testing"
COMMIT = "abcdefg"

class TestResultTestCase( unittest.TestCase ):
	"""Testcase for testing TestResults
	"""
	def setUp( self ):
		self.testresult = TestResult( TEST_MOCK, START_TIME, STOP_TIME,
									TARGET, commit=COMMIT )

	def test_serialize( self ):
		serialized = self.testresult.serialize()

		self.assertEqual( TEST_MOCK.name, serialized[ 'name' ] )
		self.assertEqual( START_TIME.isoformat( " " ), serialized[ 'started' ] )
		self.assertEqual( STOP_TIME.isoformat( " " ), serialized[ 'completed' ] )
		self.assertEqual( TARGET, serialized[ 'target' ] )
		self.assertEqual( COMMIT, serialized[ 'commit' ] )
