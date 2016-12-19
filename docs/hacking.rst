=======
Hacking
=======

Controlling CMake using scikit-build
------------------------------------

You can drive CMake directly using scikit-build::

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

See :obj:`skbuild.cmaker.CMaker` for more details.

.. _internal_api:

Internal API
------------

.. include:: modules.rst

.. _internal_cmake_modules:

Internal CMake Modules
----------------------

.. toctree::
   :maxdepth: 1

   cmake-modules/targetLinkLibrariesWithDynamicLookup
