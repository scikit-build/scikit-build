
.. _why:

===============================
Why should I use scikit-build ?
===============================

Scikit-build is a replacement for `distutils.core.Extension <https://docs.python.org/3/distutils/apiref.html?highlight=extension#distutils.core.Extension>`_
with the following advantages:

- provide better support for :doc:`additional compilers and build systems </generators>`
- first-class :ref:`cross-compilation <cross_compilation>` support
- location of dependencies and their associated build requirements

===========
Basic Usage
===========

.. _basic_usage_example:

Example of setup.py, CMakeLists.txt and pyproject.toml
------------------------------------------------------

To use scikit-build in a project, place the following in your project's
`setup.py` file::

    from skbuild import setup  # This line replaces 'from setuptools import setup'

Your project now uses scikit-build instead of setuptools.

Next, add a ``CMakeLists.txt`` to describe how to build your extension. In the following example,
a C++ extension named ``_hello`` is built::

    cmake_minimum_required(VERSION 3.11.0)
    project(hello)
    find_package(PythonExtensions REQUIRED)

    add_library(_hello MODULE hello/_hello.cxx)
    python_extension_module(_hello)
    install(TARGETS _hello LIBRARY DESTINATION hello)

Then, add a ``pyproject.toml`` to list the build system requirements::

    [build-system]
    requires = ["setuptools", "wheel", "scikit-build", "cmake", "ninja"]


.. _usage-setup_options:

Setup options
-------------

setuptools options
^^^^^^^^^^^^^^^^^^

The section below documents some of the options accepted by the ``setup()`` function.

- ``packages``: Explicitly list of all packages to include in the distribution. Setuptools will not recursively
  scan the source tree looking for any directory with an ``__init__.py`` file. To automatically generate the list
  of packages, see `Using find_package()`_.

- ``package_dir``: A mapping of package to directory names

- ``include_package_data``: If set to ``True``, this tells setuptools to automatically include any data files it finds
  inside your package directories that are specified by your ``MANIFEST.in`` file. For more information, see the setuptools
  documentation section on `Including Data Files`_.

- ``package_data``: A dictionary mapping package names to lists of glob patterns. For a complete description and examples,
  see the setuptools documentation section on `Including Data Files`_.
  You do not need to use this option if you are using include_package_data, unless you need to add e.g. files that are generated
  by your setup script and build process. (And are therefore not in source control or are files that you don’t want to include
  in your source distribution.)

- ``exclude_package_data``: Dictionary mapping package names to lists of glob patterns that should be excluded from
  the package directories. You can use this to trim back any excess files included by include_package_data.
  For a complete description and examples, see the setuptools documentation section on `Including Data Files`_.

- ``py_modules``: List all modules rather than listing packages. More details in the `Listing individual modules`_
  section of the distutils documentation.

- ``data_files``: Sequence of `(directory, files)` pairs. Each `(directory, files)` pair in the sequence specifies
  the installation directory and the files to install there. More details in the `Installing Additional Files`_
  section of the setuptools documentation.

- ``entry_points``: A dictionary mapping entry point group names to strings or lists of strings defining the entry points.
  Entry points are used to support dynamic discovery of services or plugins provided by a project.
  See `Dynamic Discovery of Services and Plugins`_ for details and examples of the format of this argument. In addition,
  this keyword is used to support `Automatic Script Creation`_.

- ``scripts``: List of python script relative paths. If the first line of the script starts with ``#!`` and contains the
  word `python`, the Distutils will adjust the first line to refer to the current interpreter location.
  More details in the `Installing Scripts <https://docs.python.org/3/distutils/setupscript.html#installing-scripts>`_ section
  of the distutils documentation.


.. _Using find_package(): https://setuptools.readthedocs.io/en/latest/setuptools.html#using-find-packages
.. _Including Data Files: https://setuptools.readthedocs.io/en/latest/setuptools.html#including-data-files
.. _Installing Additional Files: https://docs.python.org/3/distutils/setupscript.html#installing-additional-files
.. _Listing individual modules: https://docs.python.org/3/distutils/setupscript.html#listing-individual-modules
.. _Dynamic Discovery of Services and Plugins: https://setuptools.readthedocs.io/en/latest/setuptools.html#dynamic-discovery-of-services-and-plugins
.. _Automatic Script Creation: https://setuptools.readthedocs.io/en/latest/setuptools.html#automatic-script-creation


scikit-build options
^^^^^^^^^^^^^^^^^^^^

Scikit-build augments the ``setup()`` function with the following options:

- ``cmake_args``: List of `CMake options <https://cmake.org/cmake/help/v3.6/manual/cmake.1.html#options>`_.

For example::

  setup(
    [...]
    cmake_args=['-DSOME_FEATURE:BOOL=OFF']
    [...]
    )

- ``cmake_install_dir``: relative directory where the CMake artifacts are installed.
  By default, it is set to an empty string.


- ``cmake_source_dir``: Relative directory containing the project ``CMakeLists.txt``.
  By default, it is set to the top-level directory where ``setup.py`` is found.

.. _usage-cmake_with_sdist:

.. versionadded:: 0.5.0

- ``cmake_with_sdist``: Boolean indicating if CMake should be executed when
  running `sdist` command. Setting this option to ``True`` is useful when
  part of the sources specified in ``MANIFEST.in`` are downloaded by CMake.
  By default, this option is ``False``.

.. _usage-cmake_languages:

.. versionadded:: 0.7.0

- ``cmake_languages``: Tuple of languages that the project use, by default
  `('C', 'CXX',)`. This option ensures that a generator is chosen that supports
  all languages for the project.

- ``cmake_minimum_required_version``: String identifying the minimum version of CMake required
  to configure the project.

Scikit-build changes the following options:

.. versionadded:: 0.7.0

- ``setup_requires``: If ``cmake`` is found in the list, it is explicitly installed first by scikit-build.


Command line options
--------------------

::

    usage: setup.py [global_opts] cmd1 [cmd1_opts] [cmd2 [cmd2_opts] ...] [skbuild_opts] [-- [cmake_opts] [-- [build_tool_opts]]]
    or: setup.py --help [cmd1 cmd2 ...]
    or: setup.py --help-commands
    or: setup.py cmd --help


There are four types of options:

- setuptools options:

  - ``[global_opts] cmd1 [cmd1_opts] [cmd2 [cmd2_opts] ...]``
  - ``--help [cmd1 cmd2 ...]``
  - ``cmd --help``

- scikit-build options: ``[skbuild_opts]``

- CMake options: ``[cmake_opts]``

- build tool options :``[build_tool_opts]``

setuptools and scikit-build options can be passed normally, the cmake and
build_tool set of options needs to be separated by ``--``::

    Arguments following a "--" are passed directly to CMake (e.g. -DMY_VAR:BOOL=TRUE).
    Arguments following a second "--" are passed directly to  the build tool.

.. _usage-setuptools_options:

setuptools options
^^^^^^^^^^^^^^^^^^

For more details, see the `official documentation <https://setuptools.readthedocs.io/en/latest/setuptools.html#command-reference>`_.

scikit-build extends the global set of setuptools options with:

.. versionadded:: 0.4.0

::

    Global options:
      [...]
      --hide-listing      do not display list of files being included in the
                          distribution

.. versionadded:: 0.5.0

::

    Global options:
      [...]
      --force-cmake       always run CMake
      --skip-cmake        do not run CMake

.. _usage_scikit-build_options:

scikit-build options
^^^^^^^^^^^^^^^^^^^^

::

    scikit-build options:
      --build-type       specify the CMake build type (e.g. Debug or Release)
      -G , --generator   specify the CMake build system generator
      -j N               allow N build jobs at once
      [...]


.. versionadded:: 0.7.0

::

    scikit-build options:
      [...]
      --cmake-executable specify the path to the cmake executable


.. _usage_cmake_options:

CMake options
^^^^^^^^^^^^^

These are specific to CMake. See list of `CMake options <https://cmake.org/cmake/help/v3.6/manual/cmake.1.html#options>`_.

For example::

  -DSOME_FEATURE:BOOL=OFF

build tool options
^^^^^^^^^^^^^^^^^^

These are specific to the underlying build tool (e.g msbuild.exe, make, ninja).


==============
Advanced Usage
==============

Adding cmake as building requirement only if not installed or too low a version
-------------------------------------------------------------------------------

If systematically installing cmake wheel is not desired, the ``setup_requires`` list
can be set using the following approach::

    from packaging.version import LegacyVersion
    from skbuild.exceptions import SKBuildError
    from skbuild.cmaker import get_cmake_version

    # Add CMake as a build requirement if cmake is not installed or is too low a version
    setup_requires = []
    try:
        if LegacyVersion(get_cmake_version()) < LegacyVersion("3.4"):
            setup_requires.append('cmake')
    except SKBuildError:
        setup_requires.append('cmake')


.. _cross_compilation:

Cross-compilation
-----------------

See `CMake Toolchains <https://cmake.org/cmake/help/v3.6/manual/cmake-toolchains.7.html>`_.


Introduction to dockross
^^^^^^^^^^^^^^^^^^^^^^^^

.. note:: *To be documented.* See :issue:`227`.


Using dockcross-manylinux to generate Linux wheels
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note:: *To be documented.* See :issue:`227`.


Using dockcross-mingwpy to generate Windows wheels
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note:: *To be documented.* See :issue:`227`.


Examples for scikit-build developers
------------------------------------

.. note:: *To be documented.* See :issue:`227`.

    Provide small, self-contained setup function calls for (at least) two use
    cases:

    - when a `CMakeLists.txt` file already exists
    - when a user wants scikit-build to create a `CMakeLists.txt` file based
      on the user specifying some input files.
