Quickstart
=================

Installation
-----------------
.. todo::
	Running virtualenv.sh.
	Make install-virt.

Configuring Dummy
-----------------
To see how the Dummy configuration is structured, copy the ``config/default.py`` from the Dummy source directory, to the directory from which you want to run tests.
Rename ``defaults.py`` to ``dummy_config.py``.

To see which tests are passing and which are failing, we are now going to add a Pass/Fail collector to the configuration file.
Import the Pass/Fail collector by adding the following import statement under the ``import os`` line::

	from dummy.collectors.generic import PassFailCollector

Next add this collector to the list of :term:`metric` you want to collect ``METRICS``::

	METRICS = {
		# passing/failing of a test is configured as a collector
		'pass/fail': {
			'collector': PassFailCollector()
		},
	}

After running all the tests, it is often useful to have an aggregated report with an overview of all the collected metrics.
Statistics collect aggregated data over multiple tests.
Counting the number of passing and failing tests, is one generic statistic that is included with Dummy.

Let's add the counting engine as a Statistic. First import ``CountEngine`` by adding the following line under ``import os``::

	from dummy.statistics.generic import CountEngine

Next add the following to the list of configured Statistics, ``STATISTICS``::
	
	STATISTICS = {
		# we can configure what statistics are gathered over the different tests
		# several statistics engines exist in the python module `dummy.statistics.generic`

		# let's count for example the amount of tests failed/passed
		'tests passing': {
			'engine': CountEngine
		}
	}

Running Dummy
-----------------
.. todo::
	Different Dummy run commands.