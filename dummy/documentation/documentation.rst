Documentation
=============


.. _launch-options:

Launch Options
--------------------
.. todo::
	Dummy launch options.

General launch options:

Debug mode
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