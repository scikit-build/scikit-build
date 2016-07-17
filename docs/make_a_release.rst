=====================
How to Make a Release
=====================

This documents how a core developer should create a release.

0. Configure `~/.pypirc` as described
   `here <http://peterdowns.com/posts/first-time-with-pypi.html>`_.

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

6. Tag the release. Requires a GPG key with signatures. For version *X.Y.Z*::

   git tag -s -m "scikit-build X.Y.Z" X.Y.Z upstream/master

7. Upload the packages to the PyPI instance::

   twine upload dist/*

8. Check the `PyPI package page <https://pypi.python.org/pypi/scikit-build/>`_.

9. Make sure the package can be installed::

   mkvirtualenv skbuild-pip-install
   pip install scikit-build
   rmvirtualenv skbuild-pip-install

10. Update the version number in `setup.py` and `skbuild/__init__.py` and merge
    the result.

