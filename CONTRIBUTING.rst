============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

Types of Contributions
----------------------

You can contribute in many ways:

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/scikit-build/scikit-build/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug"
is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "feature"
is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

The scikit-build project could always use more documentation. We welcome help
with the official scikit-build docs, in docstrings, or even on blog posts and
articles for the web.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at
https://github.com/scikit-build/scikit-build/issues.

If you are proposing a new feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)


Get Started
-----------

Ready to contribute? Here's how to set up ``scikit-build`` for local development.

1. Fork the ``scikit-build`` repo on GitHub.

2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/scikit-build.git

   You can use the ``gh`` command line application to do these last two steps,
   as well.

3. Make sure you have ``nox`` installed using ``pipx install nox``. If you
   don't have pipx, you can install it with ``pip install pipx``. (You can
   install ``nox`` with ``pip`` instead, but nox is an application, not a
   library, and applications should always use pipx.) You can install both of
   these packages from brew on macOS/linux. You can also use ``pipx run nox``
   instead.

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass our linters and
   the tests:

    $ nox

   If you would like to check all Python versions and you don't happen to have them
   all installed locally, you can use the manylinux docker image instead:

   $ docker run --rm -itv $PWD:/src -w /src quay.io/pypa/manylinux_2_24_x86_64:latest pipx run nox

6. Commit your changes and push your branch to GitHub::

    $ git add -u .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website or the ``gh`` command line application.


Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.

2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in ``README.rst``.

3. The pull request should work for Python 3.7+ and PyPy.  Make sure that
   the tests pass for all supported Python versions in CI on your PR.


Tips
----

To run a subset of tests::

	$ nox -s tests -- tests/test_skbuild.py

You can build and serve the docs::

    $ nox -s docs -- serve

You can build an SDist and a wheel in the ``dist`` folder::

    $ nox -s build
