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

Controlling CMake using scikit-build
------------------------------------

Alternatively, you can drive CMake more directly yourself using scikit-build::

    """ Use scikit-build's `cmaker` to control CMake configuration and build.

    1. Use `cmaker` to define an object that provides convenient access to
       CMake's configure and build functionality.

    2. Use defined object, `maker`, to call `configure()` to read the
       `CMakeLists.txt` file in the current directory and generate a Makefile,
       Visual Studio solution, or whatever is appropriate for your platform.

    3. Call `make()` on the object to execute the build with the
       appropriate build tool and perform installation to the local directory.
    """
    from skbuild import cmaker
    maker = cmaker.CMaker()

    maker.configure()

    maker.make()

.. autoclass:: skbuild.cmaker.CMaker
   :members: configure, make

Examples for scikit-build developers
------------------------------------

.. note:: *To be documented.*

    Provide small, self-contained setup function calls for (at least) two use
    cases:

    - when a `CMakeLists.txt` file already exists
    - when a user wants scikit-build to create a `CMakeLists.txt` file based
      on the user specifying some input files.
