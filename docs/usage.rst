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

setuptools options
^^^^^^^^^^^^^^^^^^

For more details, see the `official documentation <https://setuptools.readthedocs.io/en/latest/setuptools.html#command-reference>`_.

.. note::

    scikit-build extends the global set of setuptools options with::

        Global options:
          [...]
          --hide-listing      do not display list of files being included in the
                              distribution

scikit-build options
^^^^^^^^^^^^^^^^^^^^

::

    scikit-build options:
      --build-type       specify the CMake build type (e.g. Debug or Release)
      -G , --generator   specify the CMake build system generator
      -j N               allow N build jobs at once


build tool options
^^^^^^^^^^^^^^^^^^

These are specific to the underlying build tool (e.g msbuild.exe, make, ninja).


Examples for scikit-build developers
------------------------------------

.. note:: *To be documented.*

    Provide small, self-contained setup function calls for (at least) two use
    cases:

    - when a `CMakeLists.txt` file already exists
    - when a user wants scikit-build to create a `CMakeLists.txt` file based
      on the user specifying some input files.
