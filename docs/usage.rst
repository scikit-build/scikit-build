
.. _why:

===============================
Why should I use scikit-build ?
===============================

Scikit-build is a replacement for `distutils.core.Extension <https://docs.python.org/3/distutils/apiref.html?highlight=extension#distutils.core.Extension>`_
with the following advantages:

- provide better support for :doc:`additional compilers and build systems </generators>`
- first-class :ref:`cross-compilation <cross_compilation>` support
- location of dependencies and their associated build requirements

=====
Usage
=====

Basic usage
-----------

To use scikit-build in a project, place the following in your project's
`setup.py` file::

    # This line replaces 'from setuptools import setup'
    from skbuild import setup

Your project now uses scikit-build instead of setuptools.

Next, add a ``CMakeLists.txt``

.. note:: *To be documented.*


.. _usage-setup_options:

Setup options
-------------

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


.. _usage_cmake_options:

CMake options
^^^^^^^^^^^^^

These are specific to CMake. See list of `CMake options <https://cmake.org/cmake/help/v3.6/manual/cmake.1.html#options>`_.

For example::

  -DSOME_FEATURE:BOOL=OFF

build tool options
^^^^^^^^^^^^^^^^^^

These are specific to the underlying build tool (e.g msbuild.exe, make, ninja).


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
