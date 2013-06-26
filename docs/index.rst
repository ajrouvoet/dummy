.. Dummy documentation master file, created by
	sphinx-quickstart on Fri May 24 11:08:55 2013.
	You can adapt this file completely to your liking, but it should at least
	contain the root `toctree` directive.

Welcome to Dummy's documentation!
=================================

Contents:

.. toctree::
	:maxdepth: 2

	quickstart
	documentation
	sourcedocs

.. todolist::

.. glossary::

	Metric
		A metric shows a certain bit of information about a test.
		An example would be the Pass/Fail metric, which contains information on the passing or failing of a test.

	Collector
		A collector gathers information to calculate a metric.
		Collectors can be configured in the ``dummy_config.py`` to collect the information.

	Statistic
		A statistic collects aggregate data on multiple tests.
		An example would be how many tests passed and failed.

	Engine
		An engine gathers the information to calculate a statistic.




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

