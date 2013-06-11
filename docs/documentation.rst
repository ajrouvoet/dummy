Documentation
=============


.. _launch-options:

Launch Options
--------------------
.. todo::
	Dummy launch options.

General launch options:

**Debug mode**
	Debug mode can be used by developers to find errors in the dummy execution::

		dummy -D <action and args>

The actions that dummy can execute are explained in the following sections.
For ``run`` see :ref:`action-run`. For ``show`` see :ref:`action-show`.

.. _action-run:

Run
^^^
Run executes tests.
Tests can be given as arguments to run::

	dummy run <test name>[, <test name 2>[, ...]

Options:

**Store**
	The results can be stored in the configured results directory with this flag::

		dummy run --store <test name>
		dummy run -s <test name>

**Suite**
	Any configured suite is can be passed by use of this flag. All tests in this suite are executed::

		dummy run --suite <suite name> [--suite <suite name2>]
		dummy run -s <suite name> [-s <suite name2>]

**Commit**
	Tests can be run on a specific commit.
	It is a committish, so it can also be a short hash or a tag name.
	Example::

		dummy run --commit <committish> <test name>
		dummy run -c <committish> <test name>

	.. note::
		This will checkout a previous commit, run the tests (of the current HEAD), and then checkout the current HEAD again.

.. _action-show:

Show
^^^^
Show previously executed and stored test results.

Options:

**Suite**
	Any configured suite is can be passed by use of this flag. All results of tests in this suite are shown::

		dummy show --suite <suite name> [--suite <suite name2>]
		dummy show -s <suite name> [-s <suite name2>]

**Commit**
	Tests can be shown from a specific commit.
	It is a committish, so it can also be a short hash or a tag name.
	Example::

		dummy show --commit <committish> <test name>
		dummy show -c <committish> <test name>

Coverage
--------
Coverage data is collected by lcov, which is a tool acting on GCC-generated coverage files.
To generate these files, add the ``--coverage`` compile-time flag to your build files.
In the respective directory containing test results, there will be a ``coverage.info`` file.
One can generate HTML output using the following command::

        genhtml coverage.info -o bam --ignore-errors source --branch-coverage

Here, ``bam`` is the output directory, and ``--branch-coverage`` indicates that lcov also outputs
branch coverage information. This can take quite some processing, and can be omitted.
