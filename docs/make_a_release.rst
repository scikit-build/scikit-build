.. _making_a_release:

================
Making a release
================

A core developer should use the following steps to create a release `X.Y.Z` of
**scikit-build** on `PyPI`_ and `Conda`_.

-------------
Prerequisites
-------------

* All CI tests are passing on `AppVeyor`_, `Azure Pipelines`_, `CircleCI`_ and `Travis CI`_.

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

1. Make sure that all CI tests are passing on `AppVeyor`_, `Azure Pipelines`_, `CircleCI`_ and `Travis CI`_.


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


5. In `README.rst`, update `PyPI`_ download count after running `this big table query <https://console.cloud.google.com/bigquery?sq=280188050539:6571a5b49fd1426395e4beea055d2b1b>`_
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
.. _Azure Pipelines: https://dev.azure.com/scikit-build/scikit-build/_build
.. _CircleCI: https://circleci.com/gh/scikit-build/scikit-build
.. _Travis CI: https://travis-ci.org/scikit-build/scikit-build/builds

.. _PyPI: https://pypi.org/project/scikit-build
.. _TestPyPI: https://test.pypi.org/project/scikit-build

-----------------------
`Conda`_: Step-by-step
-----------------------

.. warning::

   Publishing on conda requires to have corresponding the corresponding Github release.

After a GitHub release is created in the `scikit-build <https://github.com/scikit-build/scikit-build>`_ project
and after the conda-forge `Autoticking Bot <https://justcalamari.github.io/jekyll/update/2018/06/11/introduction.html>`_
creates a pull request on the `scikit-build-feedstock`_ , follow these steps to finalize the conda package
release:

1. Review and update scikit-build-feedstock pull request to include Python 3.5 support (see `here <https://github.com/conda-forge/scikit-build-feedstock/commit/abb18f5ab491e2c9392cff587bd539f876a782ae>`_ for an example)

2. Merge pull-request


In case the bot failed (e.g because of GH rate limitation) and in order to explicitly release a new version on
conda-forge, follow the steps below:

1. Choose the next release version number (that matches with the PyPI version last published)

  .. code::

    $ release=X.Y.Z

2. Fork scikit-build-feedstock

 First step is to fork `scikit-build-feedstock`_ repository.
 This is the recommended `best practice <https://conda-forge.org/docs/conda-forge_gotchas.html#using-a-fork-vs-a-branch-when-updating-a-recipe>`_  by conda.


3. Clone forked feedstock

   Fill the YOURGITHUBUSER part.

   .. code::

      $ cd /tmp && git clone https://github.com/YOURGITHUBUSER/scikit-build-feedstock.git


4. Download corresponding source for the release version

  .. code::

    $ cd /tmp && \
      wget https://github.com/NeurodataWithoutBorders/scikit-build/releases/download/$release/scikit-build-$release.tar.gz

5. Create a new branch

   .. code::

      $ cd scikit-build-feedstock && \
        git checkout -b $release


6. Modify ``meta.yaml``

   Update the `version string <https://github.com/conda-forge/scikit-build-feedstock/blob/master/recipe/meta.yaml#L2>`_ and
   `sha256 <https://github.com/conda-forge/scikit-build-feedstock/blob/master/recipe/meta.yaml#L3>`_.

   We have to modify the sha and the version string in the ``meta.yaml`` file.

   For linux flavors:

   .. code::

      $ sed -i "2s/.*/{% set version = \"$release\" %}/" recipe/meta.yaml
      $ sha=$(openssl sha256 /tmp/scikit-build-$release.tar.gz | awk '{print $2}')
      $ sed -i "3s/.*/{$ set sha256 = \"$sha\" %}/" recipe/meta.yaml

   For macOS:

   .. code::

      $ sed -i -- "2s/.*/{% set version = \"$release\" %}/" recipe/meta.yaml
      $ sha=$(openssl sha256 /tmp/scikit-build-$release.tar.gz | awk '{print $2}')
      $ sed -i -- "3s/.*/{$ set sha256 = \"$sha\" %}/" recipe/meta.yaml



7. Push the changes

   .. code::

      $ git push origin $release

8. Create a Pull Request

   Create a pull request against the `main repository <https://github.com/conda-forge/scikit-build-feedstock/pulls>`_. If the tests are passed
   a new release will be published on Anaconda cloud.


.. _Conda: https://anaconda.org/conda-forge/scikit-build
.. _scikit-build-feedstock: https://github.com/conda-forge/scikit-build-feedstock
