#!/usr/bin/env python
from setuptools import setup

setup(
	name='dummy',
	version='0.6.1',
	description='A test results framework',
	author='A.J. Rouvoet, E. Schoute and A.B. Booij',
	author_email='a.j.rouvoet_at_gmail.com',
	include_package_data=True,
	install_requires=[
    	'colorlog',
		'termcolor',
		'python-dateutil',
		'numpy',
		'matplotlib'
    ],
	packages=[
    	'dummy',
    ],
	scripts = [
    	'bin/dummy',
    ],
)
