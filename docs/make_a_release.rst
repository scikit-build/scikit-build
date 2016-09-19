=====================
How to Make a Release
=====================

A core developer should use the following steps to create a release of
**scikit-build**.

0. Configure `~/.pypirc` as described `here <http://peterdowns.com/posts/first-time-with-pypi.html>`_.

1. Make sure that all CI tests are passing.

2. Create the source tarball and binary wheels::

    git checkout master
    git fetch upstream
    git reset --hard upstream/master
    rm -rf dist/
    python setup.py sdist bdist_wheel

3. Upload the packages to the testing PyPI instance::

    twine upload -r pypitest dist/*

4. Check the `PyPI testing package page <https://testpypi.python.org/pypi/scikit-build/>`_.

5. Tag the release. Requires a GPG key with signatures. For version *X.Y.Z*::

    git tag -s -m "scikit-build X.Y.Z" X.Y.Z upstream/master

6. Upload the packages to the PyPI instance::

    twine upload dist/*

7. Check the `PyPI package page <https://pypi.python.org/pypi/scikit-build/>`_.

8. Make sure the package can be installed::

    mkvirtualenv skbuild-pip-install
    pip install scikit-build
    rmvirtualenv skbuild-pip-install

9. Update the version number in `setup.py` and `skbuild/__init__.py` and merge
   the result.

