.. _making_a_release:

================
Making a release
================

A core developer should use the following steps to create a release `X.Y.Z` of
**scikit-build** on `PyPI`_.

-------------
Prerequisites
-------------

* All CI tests are passing on `AppVeyor`_, `CircleCI`_ and `Travis CI`_.

* You have a `GPG signing key <https://help.github.com/articles/generating-a-new-gpg-key/>`_.

-------------------------
Documentation conventions
-------------------------

The commands reported below should be evaluated in the same terminal session.

Commands to evaluate starts with a dollar sign. For example::

  $ echo "Hello"
  Hello

means that ``echo "Hello"`` should be copied and evaluated in the terminal.

----------------------
Setting up environment
----------------------

1. First, `register for an account on PyPI <https://pypi.org>`_.


2. If not already the case, ask to be added as a ``Package Index Maintainer``.


3. Create a ``~/.pypirc`` file with your login credentials::

    [distutils]
    index-servers =
      pypi
      pypitest

    [pypi]
    username=<your-username>
    password=<your-password>

    [pypitest]
    repository=https://test.pypi.org/legacy/
    username=<your-username>
    password=<your-password>

  where ``<your-username>`` and ``<your-password>`` correspond to your PyPI account.


---------------------
`PyPI`_: Step-by-step
---------------------

1. Make sure that all CI tests are passing on `AppVeyor`_, `CircleCI`_ and `Travis CI`_.


2. Download the latest sources

  .. code::

    $ cd /tmp && \
      git clone git@github.com:scikit-build/scikit-build && \
      cd scikit-build


3. List all tags sorted by version

  .. code::

    $ git fetch --tags && \
      git tag -l | sort -V


4. Choose the next release version number

  .. code::

    $ release=X.Y.Z

  .. warning::

      To ensure the packages are uploaded on `PyPI`_, tags must match this regular
      expression: ``^[0-9]+(\.[0-9]+)*(\.post[0-9]+)?$``.


5. In `README.rst`, update `PyPI`_ download count after running `this big table query <https://bigquery.cloud.google.com/savedquery/280188050539:cab173ea774643c49e6f8f26234a3b08>`_
   and commit the changes.

  .. code::

    $ git add README.rst && \
      git commit -m "README: Update download stats [ci skip]"

  ..  note::

    To learn more about `pypi-stats`, see `How to get PyPI download statistics <https://kirankoduru.github.io/python/pypi-stats.html>`_.


6. In `CHANGES.rst` replace ``Next Release`` section header with
   ``Scikit-build X.Y.Z`` and commit the changes.

  .. code::

    $ git add CHANGES.rst && \
      git commit -m "Scikit-build ${release}"


7. Tag the release

  .. code::

    $ git tag --sign -m "Scikit-build ${release}" ${release} master

  .. warning::

      We recommend using a `GPG signing key <https://help.github.com/articles/generating-a-new-gpg-key/>`_
      to sign the tag.


8. Create the source distribution and wheel

  .. code::

    $ python setup.py sdist bdist_wheel


9. Publish the both release tag and the master branch

  .. code::

    $ git push origin ${release} && \
      git push origin master


10. Upload the distributions on `PyPI`_

  .. code::

    twine upload dist/*

  .. note::

    To first upload on `TestPyPI`_ , do the following::

        $ twine upload -r pypitest dist/*


11. Create a clean testing environment to test the installation

  .. code::

    $ pushd $(mktemp -d) && \
      mkvirtualenv scikit-build-${release}-install-test && \
      pip install scikit-build && \
      python -c "import skbuild"

  .. note::

    If the ``mkvirtualenv`` command is not available, this means you do not have `virtualenvwrapper`_
    installed, in that case, you could either install it or directly use `virtualenv`_ or `venv`_.

    To install from `TestPyPI`_, do the following::

        $ pip install -i https://test.pypi.org/simple scikit-build


12. Cleanup

  .. code::

    $ popd && \
      deactivate  && \
      rm -rf dist/* && \
      rmvirtualenv scikit-build-${release}-install-test


13. Add a ``Next Release`` section back in `CHANGES.rst`, commit and push local changes.

  .. code::

    $ git add CHANGES.rst && \
      git commit -m "CHANGES.rst: Add \"Next Release\" section [ci skip]" && \
      git push origin master


.. _virtualenvwrapper: https://virtualenvwrapper.readthedocs.io/
.. _virtualenv: http://virtualenv.readthedocs.io
.. _venv: https://docs.python.org/3/library/venv.html

.. _AppVeyor: https://ci.appveyor.com/project/scikit-build/scikit-build/history
.. _CircleCI: https://circleci.com/gh/scikit-build/scikit-build
.. _Travis CI: https://travis-ci.org/scikit-build/scikit-build/builds

.. _PyPI: https://pypi.org/project/scikit-build
.. _TestPyPI: https://test.pypi.org/project/scikit-build