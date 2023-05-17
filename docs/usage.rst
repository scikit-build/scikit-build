
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
The full example code is `Here <https://github.com/scikit-build/scikit-build-sample-projects/tree/master/projects/hello-cpp>`_

Make a fold name my_project as your project root folder, place the following in your project's
``setup.py`` file::

    from skbuild import setup  # This line replaces 'from setuptools import setup'
    setup(
        name="hello-cpp",
        version="1.2.3",
        description="a minimal example package (cpp version)",
        author='The scikit-build team',
        license="MIT",
        packages=['hello'],
        python_requires=">=3.7",
    )

Your project now uses scikit-build instead of setuptools.

Next, add a ``CMakeLists.txt`` to describe how to build your extension. In the following example,
a C++ extension named ``_hello`` is built::

    cmake_minimum_required(VERSION 3.18...3.22)

    project(hello)

    find_package(PythonExtensions REQUIRED)

    add_library(_hello MODULE hello/_hello.cxx)
    python_extension_module(_hello)
    install(TARGETS _hello LIBRARY DESTINATION hello)

Then, add a ``pyproject.toml`` to list the build system requirements::

    [build-system]
    requires = [
        "setuptools>=42",
        "scikit-build>=0.13",
        "cmake>=3.18",
        "ninja",
    ]
    build-backend = "setuptools.build_meta"

Make a hello folder inside my_project folder and place `_hello.cxx <https://github.com/scikit-build/scikit-build-sample-projects/blob/8fdbc8a0dd78656ea0b431e005b49f3e19786444/projects/hello-cpp/hello/_hello.cxx>`_ and `__init__.py <https://github.com/scikit-build/scikit-build-sample-projects/blob/8fdbc8a0dd78656ea0b431e005b49f3e19786444/projects/hello-cpp/hello/__init__.py>`_ inside hello folder.

Now every thing is ready, go to my_project's parent folder and type following command to install your extension::

    pip install my_project/.

If you want to see the detail of installation::

    pip install my_project/. -v

Try your new extension::

    $ python
    Python 3.10.4 (main, Jun 29 2022, 12:14:53) [GCC 11.2.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import hello
    >>> hello.hello("scikit-build")
    Hello, scikit-build!
    >>>

You can add lower limits to ``cmake`` or ``scikit-build`` as needed. Ninja
should be limited to non-Windows systems, as MSVC 2017+ ships with Ninja
already, and there are fall-backs if Ninja is missing, and the Python Ninja
seems to be less likely to find MSVC than the built-in one currently.

..  note::

    By default, scikit-build looks in the project top-level directory for a
    file named ``CMakeLists.txt``. It will then invoke ``cmake`` executable
    specifying a :doc:`generator </generators>` matching the python being used.

.. _usage-setup_options:

Setup options
-------------

setuptools options
^^^^^^^^^^^^^^^^^^

The section below documents some of the options accepted by the ``setup()``
function. These currently must be passed in your ``setup.py``, not in
``setup.cfg``, as scikit-build intercepts them and inspects them. This
restriction may be relaxed in the future. Setuptools options not listed here can
be placed in ``setup.cfg`` as normal.

- ``packages``: Explicitly list of all packages to include in the distribution. Setuptools will not recursively
  scan the source tree looking for any directory with an ``__init__.py`` file. To automatically generate the list
  of packages, see `Using find_package()`_.

- ``package_dir``: A mapping of package to directory names

- ``include_package_data``: If set to ``True``, this tells setuptools to automatically include any data files it finds
  inside your package directories that are specified by your ``MANIFEST.in`` file. For more information, see the setuptools
  documentation section on `Including Data Files`_. scikit-build matches
  `the setuptools behavior <https://setuptools.pypa.io/en/latest/history.html#id255>`__ of defaulting this parameter to
  ``True`` if a pyproject.toml file exists and contains either the ``project`` or ``tool.setuptools`` table.

- ``package_data``: A dictionary mapping package names to lists of glob patterns. For a complete description and examples,
  see the setuptools documentation section on `Including Data Files`_.
  You do not need to use this option if you are using include_package_data, unless you need to add e.g. files that are generated
  by your setup script and build process. (And are therefore not in source control or are files that you don't want to include
  in your source distribution.)

- ``exclude_package_data``: Dictionary mapping package names to lists of glob patterns that should be excluded from
  the package directories. You can use this to trim back any excess files included by include_package_data.
  For a complete description and examples, see the setuptools documentation section on `Including Data Files`_.

- ``py_modules``: List all modules rather than listing packages. More details in the `Listing individual modules`_
  section of the distutils documentation.

- ``data_files``: Sequence of ``(directory, files)`` pairs. Each ``(directory, files)`` pair in the sequence specifies
  the installation directory and the files to install there. More details in the `Installing Additional Files`_
  section of the setuptools documentation.

- ``entry_points``: A dictionary mapping entry point group names to strings or lists of strings defining the entry points.
  Entry points are used to support dynamic discovery of services or plugins provided by a project.
  See `Dynamic Discovery of Services and Plugins`_ for details and examples of the format of this argument. In addition,
  this keyword is used to support `Automatic Script Creation`_. Note that if using ``pyproject.toml`` for configuration,
  the requirement to put ``entry_points`` in ``setup.py`` also requires that the ``project`` section include ``entry_points``
  in the ``dynamic`` section.

- ``scripts``: List of python script relative paths. If the first line of the script starts with ``#!`` and contains the
  word ``python``, the Distutils will adjust the first line to refer to the current interpreter location.
  More details in the `Installing Scripts <https://docs.python.org/3/distutils/setupscript.html#installing-scripts>`_ section
  of the distutils documentation.

.. versionadded:: 0.8.0

- ``zip_safe``: A boolean indicating if the Python packages may be run directly from a zip file. If not already
  set, scikit-build sets this option to ``False``. See `Setting the zip_safe flag`_
  section of the setuptools documentation.

.. note::

    As specified in the `Wheel documentation`_, the ``universal`` and ``python-tag`` options
    have no effect.

.. _Using find_package(): https://setuptools.readthedocs.io/en/latest/setuptools.html#using-find-packages
.. _Including Data Files: https://setuptools.readthedocs.io/en/latest/setuptools.html#including-data-files
.. _Installing Additional Files: https://docs.python.org/3/distutils/setupscript.html#installing-additional-files
.. _Listing individual modules: https://docs.python.org/3/distutils/setupscript.html#listing-individual-modules
.. _Dynamic Discovery of Services and Plugins: https://setuptools.readthedocs.io/en/latest/setuptools.html#dynamic-discovery-of-services-and-plugins
.. _Automatic Script Creation: https://setuptools.readthedocs.io/en/latest/setuptools.html#automatic-script-creation
.. _Setting the zip_safe flag: https://setuptools.readthedocs.io/en/latest/setuptools.html#setting-the-zip-safe-flag
.. _Wheel documentation: https://wheel.readthedocs.io/en/stable/

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

- ``cmake_process_manifest_hook``: Python function consuming the list of files to be
  installed produced by cmake. For example, ``cmake_process_manifest_hook`` can be used
  to exclude static libraries from the built wheel.

For example::

    def exclude_static_libraries(cmake_manifest):
        return list(filter(lambda name: not (name.endswith('.a')), cmake_manifest))

    setup(
      [...]
      cmake_process_manifest_hook=exclude_static_libraries
      [...]
    )

.. _usage-cmake_with_sdist:

.. versionadded:: 0.5.0

- ``cmake_with_sdist``: Boolean indicating if CMake should be executed when
  running ``sdist`` command. Setting this option to ``True`` is useful when
  part of the sources specified in ``MANIFEST.in`` are downloaded by CMake.
  By default, this option is ``False``.

.. _usage-cmake_languages:

.. versionadded:: 0.7.0

- ``cmake_languages``: Tuple of languages that the project use, by default
  ``('C', 'CXX',)``. This option ensures that a generator is chosen that supports
  all languages for the project.

- ``cmake_minimum_required_version``: String identifying the minimum version of CMake required
  to configure the project.

- ``cmake_install_target``: Name of the target to "build" for installing the artifacts into the wheel.
  By default, this option is set to ``install``, which is always provided by CMake.
  This can be used to only install certain components.

For example::

    install(TARGETS foo COMPONENT runtime)
    add_custom_target(foo-install-runtime
        ${CMAKE_COMMAND}
        -DCMAKE_INSTALL_COMPONENT=runtime
        -P "${PROJECT_BINARY_DIR}/cmake_install.cmake"
        DEPENDS foo
        )


Scikit-build changes the following options:

.. versionadded:: 0.7.0

- ``setup_requires``: If ``cmake`` is found in the list, it is explicitly installed first by scikit-build.


Command line options
--------------------

Warning: Passing options to ``setup.py`` is deprecated and may be removed in a
future release. Environment variables can be used instead for most options.

::

    usage: setup.py [global_opts] cmd1 [cmd1_opts] [cmd2 [cmd2_opts] ...] [skbuild_opts] [cmake_configure_opts] [-- [cmake_opts] [-- [build_tool_opts]]]
    or: setup.py --help [cmd1 cmd2 ...]
    or: setup.py --help-commands
    or: setup.py cmd --help


There are few types of options:

- :ref:`setuptools options <usage-setuptools_options>`:

  - ``[global_opts] cmd1 [cmd1_opts] [cmd2 [cmd2_opts] ...]``
  - ``--help [cmd1 cmd2 ...]``
  - ``cmd --help``

- :ref:`scikit-build options <usage_scikit-build_options>`: ``[skbuild_opts]``

- :ref:`CMake configure options <usage_cmake_configure_options>`: ``[cmake_configure_opts]``

- :ref:`CMake options <usage_cmake_options>`: ``[cmake_opts]``

- :ref:`build tool options<usage_build_tool_options>`:``[build_tool_opts]``

setuptools, scikit-build and CMake configure options can be passed normally, the cmake and
build_tool set of options needs to be separated by ``--``::

    Arguments following a "--" are passed directly to CMake (e.g. -DSOME_FEATURE:BOOL=ON).
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

.. note::

    As specified in the `Wheel documentation`_, the ``--universal`` and ``--python-tag`` options
    have no effect.


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


.. versionadded:: 0.8.0

::

    scikit-build options:
      [...]
      --skip-generator-test  skip generator test when a generator is explicitly selected using --generator


.. _usage_cmake_configure_options:

CMake Configure options
^^^^^^^^^^^^^^^^^^^^^^^

.. versionadded:: 0.10.1

These options are relevant when configuring a project and can be passed as global options using ``setup.py``
or ``pip install``.

The CMake options accepted as global options are any of the following:

::

    -C<initial-cache>            = Pre-load a script to populate the cache.
    -D<var>[:<type>]=<value>     = Create or update a cmake cache entry.


.. warning::

    The CMake configure option should be passed without spaces. For example, use `-DSOME_FEATURE:BOOL=ON` instead
    of `-D SOME_FEATURE:BOOL=ON`.


.. _usage_cmake_options:

CMake options
^^^^^^^^^^^^^

These are any specific to CMake. See list of `CMake options <https://cmake.org/cmake/help/v3.6/manual/cmake.1.html#options>`_.

For example::

  -DSOME_FEATURE:BOOL=OFF


.. _usage_build_tool_options:

build tool options
^^^^^^^^^^^^^^^^^^

These are specific to the underlying build tool (e.g msbuild.exe, make, ninja).


==============
Advanced Usage
==============

How to test if scikit-build is driving the compilation ?
--------------------------------------------------------

To support the case of code base being built as both a standalone project
and a python wheel, it is possible to test for the variable ``SKBUILD``:

.. code-block:: cmake

    if(SKBUILD)
      message(STATUS "The project is built using scikit-build")
    endif()

Adding cmake as building requirement only if not installed or too low a version
-------------------------------------------------------------------------------

If systematically installing cmake wheel is not desired, it is possible to set it using an ``in-tree backend``.
For this purpose place the following configuration in your ``pyproject.toml``::

    [build-system]
    requires = [
      "setuptools>=42",
      "packaging",
      "scikit-build",
      "ninja; platform_system!='Windows'"
    ]
    build-backend = "backend"
    backend-path = ["_custom_build"]

then you can implement a thin wrapper around ``build_meta`` in the ``_custom_build/backend.py`` file::

    from setuptools import build_meta as _orig

    prepare_metadata_for_build_wheel = _orig.prepare_metadata_for_build_wheel
    build_wheel = _orig.build_wheel
    build_sdist = _orig.build_sdist
    get_requires_for_build_sdist = _orig.get_requires_for_build_sdist

    def get_requires_for_build_wheel(config_settings=None):
        from packaging import version
        from skbuild.exceptions import SKBuildError
        from skbuild.cmaker import get_cmake_version
        packages = []
        try:
            if version.parse(get_cmake_version()) < version.parse("3.4"):
                packages.append('cmake')
        except SKBuildError:
            packages.append('cmake')

        return _orig.get_requires_for_build_wheel(config_settings) + packages

Also see `scikit-build-core <https://scikit-build-core.readthedocs.io>`_ where
this is a built-in feature.

.. _usage_enabling_parallel_build:

Enabling parallel build
-----------------------

Ninja
^^^^^

If :ref:`Ninja` generator is used, the associated build tool (called ``ninja``)
will automatically parallelize the build based on the number of available CPUs.

To limit the number of parallel jobs, the build tool option ``-j N`` can be passed
to ``ninja``.

For example, to  limit the number of parallel jobs to ``3``, the following could be done::

    python setup.py bdist_wheel -- -- -j3

For complex projects where more granularity is required, it is also possible to limit
the number of simultaneous link jobs, or compile jobs, or both.

Indeed, starting with CMake 3.11, it is possible to configure the project with these
options:

* `CMAKE_JOB_POOL_COMPILE <https://cmake.org/cmake/help/latest/variable/CMAKE_JOB_POOL_COMPILE.html>`_
* `CMAKE_JOB_POOL_LINK <https://cmake.org/cmake/help/latest/variable/CMAKE_JOB_POOL_LINK.html>`_
* `CMAKE_JOB_POOLS <https://cmake.org/cmake/help/latest/variable/CMAKE_JOB_POOLS.html>`_

For example, to have at most ``5`` compile jobs and ``2`` link jobs, the following could be done::

    python setup.py bdist_wheel -- \
      -DCMAKE_JOB_POOL_COMPILE:STRING=compile \
      -DCMAKE_JOB_POOL_LINK:STRING=link \
      '-DCMAKE_JOB_POOLS:STRING=compile=5;link=2'

Unix Makefiles
^^^^^^^^^^^^^^

If :ref:`Unix Makefiles` generator is used, the associated build tool (called ``make``)
will **NOT** automatically parallelize the build, the user has to explicitly pass
option like ``-j N``.

For example, to limit the number of parallel jobs to ``3``, the following could be done::

    python setup.py bdist_wheel -- -- -j3


Visual Studio IDE
^^^^^^^^^^^^^^^^^

If :ref:`Visual Studio IDE` generator is used, there are two types of parallelism:

* target level parallelism
* object level parallelism

.. warning::

    Since finding the right combination of parallelism can be challenging, whenever
    possible we recommend to use the `Ninja`_ generator.


To adjust the object level parallelism, the compiler flag ``/MP[processMax]`` could
be specified. To learn more, read `/MP (Build with Multiple Processes)
<https://docs.microsoft.com/en-us/cpp/build/reference/mp-build-with-multiple-processes>`_.

For example::

    set CXXFLAGS=/MP4
    python setup.py bdist_wheel

The target level parallelism can be set from command line
using ``/maxcpucount:N``. This defines the number of simultaneous ``MSBuild.exe`` processes.
To learn more, read `Building Multiple Projects in Parallel with MSBuild
<https://msdn.microsoft.com/en-us/library/bb651793.aspx>`_.

For example::

    python setup.py bdist_wheel -- -- /maxcpucount:4


.. _support_isolated_build:

Support for isolated build
--------------------------

.. versionadded:: 0.8.0

As specified in `PEP 518`_, dependencies required at install time can be specified using a
``pyproject.toml`` file. Starting with pip 10.0, pip reads the ``pyproject.toml`` file and
installs the associated dependencies in an isolated environment. See the `pip build system interface`_
documentation.

An isolated environment will be created when using pip to install packages directly from
source or to create an editable installation.

scikit-build supports these use cases as well as the case where the isolated environment support
is explicitly disabled using the pip option ``--no-build-isolation`` available with the ``install``,
``download`` and ``wheel`` commands.

.. _PEP 518: https://www.python.org/dev/peps/pep-0518/
.. _pip build system interface: https://pip.pypa.io/en/stable/reference/pip/#build-system-interface


.. _optimized_incremental_build:

Optimized incremental build
---------------------------

To optimize the developer workflow, scikit-build reconfigures the CMake project only when
needed. It caches the environment associated with the generator as well as the CMake execution
properties.

The CMake properties are saved in a :func:`CMake spec file <skbuild.constants.CMAKE_SPEC_FILE()>` responsible
to store the CMake executable path, the CMake configuration arguments, the CMake version as well as the
environment variables ``PYTHONNOUSERSITE`` and ``PYTHONPATH``.

If there are no ``CMakeCache.txt`` file or if any of the CMake properties changes, scikit-build will
explicitly reconfigure the project calling :meth:`skbuild.cmaker.CMaker.configure`.

If a file is added to the CMake build system by updating one of the ``CMakeLists.txt`` file, scikit-build
will not explicitly reconfigure the project. Instead, the generated build-system will automatically
detect the change and reconfigure the project after :meth:`skbuild.cmaker.CMaker.make` is called.


Environment variable configuration
----------------------------------

Scikit-build support environment variables to configure some options. These are:

``SKBUILD_CONFIGURE_OPTIONS``/``CMAKE_ARGS``
  This will add configuration options when configuring CMake.
  ``SKBUILD_CONFIGURE_OPTIONS`` will be used instead of ``CMAKE_ARGS`` if both
  are defined.

``SKBUILD_BUILD_OPTIONS``
  Pass options to the build.


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
