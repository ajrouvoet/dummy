#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
	name='dummy',
	version='1.0.0',
	description='A test results framework',
	author='A.J. Rouvoet, E. Schoute and A.B. Booij',
	author_email='a.j.rouvoet_at_gmail.com',
	license='MIT',
	keywords = 'test testing results framework',
	include_package_data=True,
	install_requires=[
    	'colorlog',
		'termcolor',
		'python-dateutil',
    ],
    extras_require={
    	'plot': [ 'numpy>=1.4.1', 'matplotlib' ]
    },
	packages=find_packages(),
	entry_points = {
		'console_scripts': [
			'dummy = dummy.__main__:main'
		]
    }
)
