=====================
How to Make a Release
=====================

A core developer should use the following steps to create a release `X.Y.Z` of
**scikit-build**.

0. Configure `~/.pypirc` as described `here <https://packaging.python.org/distributing/#uploading-your-project-to-pypi>`_.

1. Make sure that all CI tests are passing.

2. Update version numbers and download count:

  * in `setup.py` and `skbuild/__init__.py`

  * in `CHANGES.rst` by changing ``Next Release`` section header with
    ``Scikit-build X.Y.Z``.

  * run `this big table query <https://bigquery.cloud.google.com/savedquery/282424744644:d13dae955ff540cfafd2fddf8190962a>`_
    and update the pypi download count in ``README.rst``. To learn more about `pypi-stats`,
    see `How to get PyPI download statistics <https://kirankoduru.github.io/python/pypi-stats.html>`_.

3. Commit the changes using title ``scikit-build X.Y.Z``.

3. Create the source tarball and binary wheels::

    git checkout master
    git fetch upstream
    git reset --hard upstream/master
    rm -rf dist/
    python setup.py sdist bdist_wheel

4. Upload the packages to the testing PyPI instance::

    twine upload --sign -r pypitest dist/*

5. Check the `PyPI testing package page <https://testpypi.python.org/pypi/scikit-build/>`_.

6. Tag the release. Requires a GPG key with signatures. For version *X.Y.Z*::

    git tag -s -m "scikit-build X.Y.Z" X.Y.Z upstream/master

7. Upload the packages to the PyPI instance::

    twine upload --sign dist/*

8. Check the `PyPI package page <https://pypi.python.org/pypi/scikit-build/>`_.

9. Make sure the package can be installed::

    mkvirtualenv skbuild-pip-install
    pip install scikit-build
    rmvirtualenv skbuild-pip-install

10. Add a ``Next Release`` section back in `CHANGES.rst` and merge the result.

11. Push local changes
