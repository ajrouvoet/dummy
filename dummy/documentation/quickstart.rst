Quickstart
=================
This chapter will describe how to quickly get Dummy up and running.

Installation
-----------------
.. todo::
	Running virtualenv.sh.
	Make install-virt.

Tests have to be configured in a certain way for Dummy.
The common testing folder is setup using the following::

	+ tests/
	|	- run.sh
	|	+ <test name>/
	|	|	makefile
	|	+ <test name 2>/
	|	+ ...

The ``run.sh`` gets the test folder passed as first argument.
In the common case the ``run.sh`` executes a ``make clean`` and ``make`` in the given folder.
See for an example :download:`this example run.sh <code/run.sh>`.
This way Dummy is independent of the specific testing method, because it can be implemented by the developer himself.

Configuring Dummy
-----------------
To see how the Dummy configuration is structured, copy the ``config/default.py`` from the Dummy source directory, to the directory from which you want to run tests.
Rename ``defaults.py`` to ``dummy_config.py``.

To see which tests are passing and which are failing, we are now going to add a Pass/Fail collector to the configuration file.
Import the Pass/Fail collector by adding the following import statement under the ``import os`` line::

	from dummy.collectors.generic import PassFailCollector

Next add this :term:`collector` to the list of :term:`metric` you want to collect ``METRICS``::

	METRICS = {
		# passing/failing of a test is configured as a collector
		'pass/fail': {
			'collector': PassFailCollector()
		},
	}

After running all the tests, it is often useful to have an aggregated report with an overview of all the collected metrics.
A :term:`statistic` collects aggregated data over multiple tests.
Counting the number of passing and failing tests, is one generic statistic that is included with Dummy.

Let's add the counting :term:`engine` as a Statistic. First import ``CountEngine`` by adding the following line under ``import os``::

	from dummy.statistics.generic import CountEngine

Next add the following to the list of configured Statistics, ``STATISTICS``::
	
	STATISTICS = {
		# we can configure what statistics are gathered over the different tests
		# several statistics engines exist in the python module `dummy.statistics.generic`

		# let's count for example the amount of tests failed/passed
		'tests passing': {
			'engine': CountEngine
		},
	}

The configuration file should look like :download:`this example dummy_config.py <code/example_dummy_config.py>`.

Running Dummy
-----------------
Time to run Dummy on the tests.
Let's start with running a single test, execute the following with ``<test name>`` the name of a test in the test directory::

	dummy run <test name>

This will output the test results to the console. When you also want to save the results, add the ``--store`` (or ``-s``) flag::

	dummy run --store <test name>

This will create the results directory (if it didn't exist yet), which has the following folder structure::

	+ <git committish>/
	|	+ <test name>/
	|	|	- results.json
	|	|	- ...

The ``results.json`` file contains a JSON structured results overview.
If you want to review previously run tests run::

	dummy show <test name>

It is also possible to configure test suites by adding the ``--suite`` (or ``-s``) flag.
By default the ``all`` suite is configured to run all the tests in the test directory.
This suite can be run by running the following (the ``-s`` flag is optional)::

	dummy run -[s]S all

The results for an entires suite can be viewed with the followig command::

	dummy show -S all

.. seealso::
	The complete documentation contains more extensive explanation on the launch options, see :ref:`launch-options`