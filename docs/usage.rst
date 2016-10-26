=====
Usage
=====

Basic usage
-----------

To use scikit-build in a project, place the following in your project's
`setup.py` file::

    # This line replaces 'from setuptools import setup'
    from skbuild import setup

Now, your project will use scikit-build instead of setuptools.

Examples for scikit-build developers
------------------------------------

.. note:: *To be documented.*

    Provide small, self-contained setup function calls for (at least) two use
    cases:

    - when a `CMakeLists.txt` file already exists
    - when a user wants scikit-build to create a `CMakeLists.txt` file based
      on the user specifying some input files.
