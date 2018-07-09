=====================
How to Make a Release
=====================

A core developer should use the following steps to create a release `X.Y.Z` of
**scikit-build**.

0. Configure `~/.pypirc` as described `here <https://packaging.python.org/distributing/#uploading-your-project-to-pypi>`_.

1. Make sure that all CI tests are passing: `AppVeyor <https://ci.appveyor.com/project/scikit-build/scikit-build>`_,
   `CircleCI <https://circleci.com/gh/scikit-build/scikit-build>`_
   and `TravisCi <https://travis-ci.org/scikit-build/scikit-build>`_.

2. Update version numbers and download count:

  * in `setup.py` and `skbuild/__init__.py`

  * in `CHANGES.rst` by changing ``Next Release`` section header with
    ``Scikit-build X.Y.Z``.

  * run `this big table query <https://bigquery.cloud.google.com/savedquery/280188050539:cab173ea774643c49e6f8f26234a3b08>`_
    and update the pypi download count in ``README.rst``. To learn more about `pypi-stats`,
    see `How to get PyPI download statistics <https://kirankoduru.github.io/python/pypi-stats.html>`_.

3. Commit the changes using title ``scikit-build X.Y.Z``.

4. Create the source tarball and binary wheels::

    git checkout master
    git fetch upstream
    git reset --hard upstream/master
    rm -rf dist/
    python setup.py sdist bdist_wheel

5. Upload the packages to the testing PyPI instance::

    twine upload --sign -r pypitest dist/*

6. Check the `PyPI testing package page <https://testpypi.python.org/pypi/scikit-build/>`_.

7. Tag the release. Requires a GPG key with signatures. For version *X.Y.Z*::

    git tag -s -m "scikit-build X.Y.Z" X.Y.Z upstream/master

8. Upload the packages to the PyPI instance::

    twine upload --sign dist/*

9. Check the `PyPI package page <https://pypi.python.org/pypi/scikit-build/>`_.

10. Make sure the package can be installed::

    mkvirtualenv skbuild-pip-install
    pip install scikit-build
    rmvirtualenv skbuild-pip-install

11. Add a ``Next Release`` section back in `CHANGES.rst` and merge the result.

12. Push local changes
