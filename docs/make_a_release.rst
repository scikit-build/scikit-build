.. _making_a_release:

================
Making a release
================

A core developer should use the following steps to create a release ``X.Y.Z`` of
**scikit-build** on `PyPI`_ and `Conda`_.

-------------
Prerequisites
-------------

* All CI tests are passing on `GitHub Actions`_.

* You can push to the repository and create GitHub releases. No PyPI
  credentials are needed: publishing the GitHub release triggers a GitHub
  Actions workflow that builds the package and uploads it to `PyPI`_ using
  trusted publishing.

-------------------------
Documentation conventions
-------------------------

The commands reported below should be evaluated in the same terminal session.

Commands to evaluate starts with a dollar sign. For example::

  $ echo "Hello"
  Hello

means that ``echo "Hello"`` should be copied and evaluated in the terminal.

---------------------
`PyPI`_: Step-by-step
---------------------

1. Make sure that all CI tests are passing on `GitHub Actions`_.


2. Download the latest sources (or use an existing git checkout)

  .. code::

    $ cd /tmp && \
      git clone git@github.com:scikit-build/scikit-build && \
      cd scikit-build


3. List all tags sorted by creation date

  .. code::

    $ git tag -l --sort creatordate


4. Choose the next release version number

  .. code::

    $ release=X.Y.Z

  .. note::

      Tags are bare :pep:`440` versions with no ``v`` prefix: ``1.0.0``,
      ``1.0.0rc1``, ``1.0.0.post1``. The version is derived from the tag by
      hatch-vcs.


5. In ``CHANGES.md`` replace ``Next Release`` section header with
   ``Scikit-build X.Y.Z`` and commit the changes. Keep the
   ``START-BRIEF-CHANGELOG`` marker above the newest release section so the
   release notes appear in the PyPI readme.

  .. code::

    $ git add CHANGES.md && \
      git commit -m "Scikit-build $release"


6. Tag the release

  .. code::

    $ git tag -a -m "Scikit-build $release" $release main


7. Publish both the release tag and the main branch

  .. code::

    $ git push origin $release && \
      git push origin main


8. Make a `GitHub release <https://github.com/scikit-build/scikit-build/releases/new>`_.
   Paste the release's section from ``CHANGES.md`` as the body. The ``{pr}`` and
   ``{user}`` roles should be converted to simple ``#<number>`` and ``@<user>``
   form. Be sure to use the tag you just pushed as the tag version, and
   ``Scikit-build X.Y.Z`` should be the name. For a release candidate, check
   the "Set as a pre-release" box so it does not become the latest release.

  .. note::

    For examples of releases, see https://github.com/scikit-build/scikit-build/releases

  Publishing the release triggers the ``CD`` GitHub Actions workflow, which
  builds the SDist and wheel and uploads them to `PyPI`_.


9. Add a ``Next Release`` section back in ``CHANGES.md``, commit and push local changes.

  .. code::

    $ git add CHANGES.md && \
      git commit -m "CHANGES.md: Add \"Next Release\" section [ci skip]" && \
      git push origin main



10. Add an entry to the ``Announcements`` category of the `scikit-build discussions board`_.

  .. note::

    For examples of announcements, see https://github.com/orgs/scikit-build/discussions/categories/announcements


.. _GitHub Actions: https://github.com/scikit-build/scikit-build/actions

.. _PyPI: https://pypi.org/project/scikit-build

.. _scikit-build discussions board: https://github.com/orgs/scikit-build/discussions/categories/announcements

-----------------------
`Conda`_: Step-by-step
-----------------------

.. warning::

   Publishing on conda requires the corresponding GitHub release.

After a GitHub release is created in the `scikit-build <https://github.com/scikit-build/scikit-build>`_ project
and after the conda-forge `Autoticking Bot <https://justcalamari.github.io/jekyll/update/2018/06/11/introduction.html>`_
creates a pull request on the `scikit-build-feedstock`_ , follow these steps to finalize the conda package
release:

1. Review the pull-request

2. Merge pull-request


In case the bot failed (e.g because of GH rate limitation) and in order to explicitly release a new version on
conda-forge, follow the steps below:

1. Choose the next release version number (that matches with the PyPI version last published)

  .. code::

    $ release=X.Y.Z

2. Fork scikit-build-feedstock

 First step is to fork `scikit-build-feedstock`_ repository.
 This is the recommended `best practice <https://conda-forge.org/docs/maintainer/updating_pkgs.html>`_  by conda.


3. Clone forked feedstock

   Fill the YOURGITHUBUSER part.

   .. code::

      $ YOURGITHUBUSER=user
      $ cd /tmp && git clone https://github.com/$YOURGITHUBUSER/scikit-build-feedstock.git


4. Download corresponding source for the release version

  .. code::

    $ cd /tmp && \
      wget https://github.com/scikit-build/scikit-build/archive/$release.tar.gz


5. Create a new branch

   .. code::

      $ cd scikit-build-feedstock && \
        git checkout -b $release


6. Modify ``meta.yaml``

   Update the `version string <https://github.com/conda-forge/scikit-build-feedstock/blob/main/recipe/meta.yaml#L2>`_ and
   `sha256 <https://github.com/conda-forge/scikit-build-feedstock/blob/main/recipe/meta.yaml#L3>`_.

   We have to modify the sha and the version string in the ``meta.yaml`` file.

   For linux flavors:

   .. code::

      $ sed -i "1s/.*/{% set version = \"$release\" %}/" recipe/meta.yaml && \
        sha=$(openssl sha256 /tmp/$release.tar.gz | awk '{print $2}') && \
        sed -i "2s/.*/{% set sha256 = \"$sha\" %}/" recipe/meta.yaml

   For macOS:

   .. code::

      $ sed -i -- "1s/.*/{% set version = \"$release\" %}/" recipe/meta.yaml && \
        sha=$(openssl sha256 /tmp/$release.tar.gz | awk '{print $2}') && \
        sed -i -- "2s/.*/{% set sha256 = \"$sha\" %}/" recipe/meta.yaml

   Commit local changes.

   .. code::

      $ git add recipe/meta.yaml && \
          git commit -m "scikit-build v$release version"


7. Push the changes

   .. code::

      $ git push origin $release

8. Create a Pull Request

   Create a pull request against the `main repository <https://github.com/conda-forge/scikit-build-feedstock/pulls>`_. If the tests are passed
   a new release will be published on Anaconda cloud.


.. _Conda: https://anaconda.org/conda-forge/scikit-build
.. _scikit-build-feedstock: https://github.com/conda-forge/scikit-build-feedstock
