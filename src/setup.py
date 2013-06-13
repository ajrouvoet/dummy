#!/usr/bin/env python

from setuptools import setup

setup(
		name='Dummy',
		version='0.5',
		description='A generic testing framework',
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
    		'scripts/dummy.sh',
    		],
		)
