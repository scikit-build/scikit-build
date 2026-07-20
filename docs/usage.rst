
.. _why:

===============================
Why should I use scikit-build ?
===============================

Scikit-build is a replacement for `distutils.core.Extension <https://docs.python.org/3/distutils/apiref.html?highlight=extension#distutils.core.Extension>`_
with the following advantages:

- provide better support for :doc:`additional compilers and build systems </generators>`
- first-class :ref:`cross-compilation <cross_compilation>` support
- location of dependencies and their associated build requirements

.. _migration_guide:

.. _usage-cmake_with_sdist:

.. _usage-cmake_languages:

.. _usage_cmake_configure_options:

.. _usage_cmake_options:

===============================
Migrating from scikit-build 0.x
===============================

Starting with scikit-build 1.0, the classic scikit-build backend was replaced
by the setuptools plugin provided by `scikit-build-core
<https://scikit-build-core.readthedocs.io>`_. ``skbuild.setup()`` is now a
thin wrapper around ``scikit_build_core.setuptools.wrapper.setup()``. Most
projects keep working unchanged:

- ``from skbuild import setup`` with the ``cmake_args``, ``cmake_source_dir``,
  ``cmake_install_dir``, ``cmake_install_target`` and
  ``cmake_process_manifest_hook`` keyword arguments.
- The CMake modules shipped with scikit-build, like
  ``find_package(PythonExtensions)``, ``find_package(Cython)``,
  ``find_package(NumPy)`` and ``find_package(F2PY)``. They are now injected
  into ``CMAKE_MODULE_PATH`` using scikit-build-core's ``cmake.module``
  entry-point group.
- The ``SKBUILD`` CMake variable is still set, now to ``2`` instead of
  ``TRUE`` (still truthy).
- The standard setuptools commands: ``build``, ``bdist_wheel``, ``sdist``,
  ``install`` and ``build_ext --inplace``.
- The recommended ``build-system`` table in ``pyproject.toml`` is unchanged:
  ``requires = ["setuptools", "scikit-build", "cmake", "ninja"]`` with
  ``build-backend = "setuptools.build_meta"``.

The following changes are breaking:

- All scikit-build-specific command line options were removed:
  ``--build-type``, ``-G``/``--generator``, ``-j N``, ``--cmake-executable``,
  ``--skip-generator-test``, ``--hide-listing``, ``--force-cmake``,
  ``--skip-cmake``, ``--install-target``, as well as the
  ``setup.py <setuptools args> -- <cmake args> -- <build tool args>``
  triple-section syntax. Use the ``CMAKE_ARGS`` and ``CMAKE_GENERATOR``
  environment variables, the ``cmake_args`` keyword of ``setup()``,
  scikit-build-core's ``[tool.scikit-build]`` settings in ``pyproject.toml``
  (or the equivalent ``SKBUILD_*`` environment variables), or the options of
  the new ``build_cmake`` setuptools command (``--source-dir``,
  ``--cmake-args``, ``--parallel`` and ``--debug``) instead. See the
  `scikit-build-core configuration documentation
  <https://scikit-build-core.readthedocs.io/en/latest/configuration/index.html>`__.

- ``cmake_with_sdist=True`` now raises an error. ``cmake_languages`` and
  ``cmake_minimum_required_version`` are accepted but ignored with a warning;
  the minimum CMake version is configured with the ``cmake.version`` setting
  in the ``[tool.scikit-build]`` table of ``pyproject.toml``.

- The Python modules ``skbuild.cmaker``, ``skbuild.constants``,
  ``skbuild.command.*``, ``skbuild.platform_specifics``, ``skbuild.utils``
  and ``skbuild.setuptools_wrap`` no longer exist.
  ``skbuild.exceptions.SKBuildError`` is now an alias of setuptools'
  ``SetupError``.

- The ``_skbuild/<platform>-<pyversion>/`` build directory is gone; the
  standard setuptools ``build/`` directories are used instead (CMake builds
  in an ``_skbuild`` directory under ``build/temp.*``).

- sdists no longer automatically generate their file manifest from git;
  provide a ``MANIFEST.in`` (or use ``setuptools-scm``) like any other
  setuptools project.

- Editable installs (``pip install -e .``) require setting
  ``editable.mode = "inplace"`` in the ``[tool.scikit-build]`` table of
  ``pyproject.toml``. A plain ``setup.py build_ext --inplace`` still works
  without configuration.

- Generators are no longer discovered by probing for Visual Studio and
  running a language test; CMake's own default generator selection applies.
  Set the ``CMAKE_GENERATOR`` environment variable to override it. See
  :doc:`/generators`.

- scikit-build now depends on ``scikit-build-core[setuptools]`` at run time;
  the ``distro``, ``wheel`` and ``tomli`` dependencies were dropped.

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
        python_requires=">=3.8",
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
already.

..  note::

    By default, scikit-build looks in the project top-level directory for a
    file named ``CMakeLists.txt``. It will then invoke the ``cmake``
    executable, using CMake's default :doc:`generator </generators>` unless
    the ``CMAKE_GENERATOR`` environment variable is set.

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

- ``cmake_install_target``: Name of the target to "build" for installing the
  artifacts into the wheel. By default, this option is set to ``install``,
  which is always provided by CMake and runs ``cmake --install``. Any other
  value is installed by building that target with ``cmake --build --target``,
  which can be used to only install certain components.

For example::

    install(TARGETS foo COMPONENT runtime)
    add_custom_target(foo-install-runtime
        ${CMAKE_COMMAND}
        -DCMAKE_INSTALL_COMPONENT=runtime
        -P "${PROJECT_BINARY_DIR}/cmake_install.cmake"
        DEPENDS foo
        )

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

.. versionchanged:: 1.0

    The ``cmake_with_sdist`` option now raises an error if set to ``True``,
    and the ``cmake_languages`` and ``cmake_minimum_required_version`` options
    are ignored with a warning. See :ref:`migration_guide`.


.. _usage-setuptools_options:

Command line options
--------------------

.. versionchanged:: 1.0

    The scikit-build-specific command line options and the
    ``setup.py <setuptools args> -- <cmake args> -- <build tool args>``
    syntax were removed. See :ref:`migration_guide`.

Only the standard `setuptools command line options
<https://setuptools.readthedocs.io/en/latest/setuptools.html#command-reference>`_
are supported. CMake options can be passed using the ``CMAKE_ARGS``
environment variable, the ``cmake_args`` keyword of ``setup()``, or
scikit-build-core's ``[tool.scikit-build]`` settings in ``pyproject.toml``.

In addition, the ``build_cmake`` command accepts the ``--source-dir``,
``--cmake-args``, ``--parallel`` and ``--debug`` options. For example::

    python setup.py build_cmake --cmake-args="-DSOME_FEATURE:BOOL=OFF" --parallel 3

.. note::

    As specified in the `Wheel documentation`_, the ``--universal`` and ``--python-tag`` options
    have no effect.


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

.. versionchanged:: 1.0

    The ``SKBUILD`` variable is now set to ``2`` instead of ``TRUE``. Both
    values are truthy in CMake.

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

    import re
    import subprocess

    from setuptools import build_meta as _orig

    prepare_metadata_for_build_wheel = _orig.prepare_metadata_for_build_wheel
    build_wheel = _orig.build_wheel
    build_sdist = _orig.build_sdist
    get_requires_for_build_sdist = _orig.get_requires_for_build_sdist

    def get_requires_for_build_wheel(config_settings=None):
        from packaging import version
        packages = []
        try:
            output = subprocess.run(
                ["cmake", "--version"], check=True, capture_output=True, text=True
            ).stdout
            cmake_version = re.match(r"cmake version (\S+)", output).group(1)
            if version.parse(cmake_version) < version.parse("3.15"):
                packages.append('cmake')
        except (OSError, subprocess.CalledProcessError, AttributeError):
            packages.append('cmake')

        return _orig.get_requires_for_build_wheel(config_settings) + packages

Also see `scikit-build-core <https://scikit-build-core.readthedocs.io>`_ where
this is a built-in feature.

.. _usage_enabling_parallel_build:

Enabling parallel build
-----------------------

.. _Ninja:

Ninja
^^^^^

If the ``Ninja`` generator is used, the associated build tool (called ``ninja``)
will automatically parallelize the build based on the number of available CPUs.

To limit the number of parallel jobs, set the ``CMAKE_BUILD_PARALLEL_LEVEL``
environment variable, or pass the ``--parallel`` option to the ``build_cmake``
command.

For example, to  limit the number of parallel jobs to ``3``, the following could be done::

    python setup.py build_cmake --parallel 3

For complex projects where more granularity is required, it is also possible to limit
the number of simultaneous link jobs, or compile jobs, or both.

Indeed, starting with CMake 3.11, it is possible to configure the project with these
options:

* `CMAKE_JOB_POOL_COMPILE <https://cmake.org/cmake/help/latest/variable/CMAKE_JOB_POOL_COMPILE.html>`_
* `CMAKE_JOB_POOL_LINK <https://cmake.org/cmake/help/latest/variable/CMAKE_JOB_POOL_LINK.html>`_
* `CMAKE_JOB_POOLS <https://cmake.org/cmake/help/latest/variable/CMAKE_JOB_POOLS.html>`_

For example, to have at most ``5`` compile jobs and ``2`` link jobs, the following could be done::

    export CMAKE_ARGS="-DCMAKE_JOB_POOL_COMPILE:STRING=compile \
      -DCMAKE_JOB_POOL_LINK:STRING=link \
      -DCMAKE_JOB_POOLS:STRING=compile=5;link=2"
    python setup.py bdist_wheel

Unix Makefiles
^^^^^^^^^^^^^^

If the ``Unix Makefiles`` generator is used, the associated build tool (called ``make``)
will **NOT** automatically parallelize the build, the user has to explicitly set
the number of jobs.

For example, to limit the number of parallel jobs to ``3``, the following could be done::

    CMAKE_BUILD_PARALLEL_LEVEL=3 python setup.py bdist_wheel


.. _Visual Studio IDE:

Visual Studio IDE
^^^^^^^^^^^^^^^^^

If a ``Visual Studio`` generator is used, there are two types of parallelism:

* target level parallelism
* object level parallelism

.. warning::

    Since finding the right combination of parallelism can be challenging, whenever
    possible we recommend to use the ``Ninja`` generator.


To adjust the object level parallelism, the compiler flag ``/MP[processMax]`` could
be specified. To learn more, read `/MP (Build with Multiple Processes)
<https://docs.microsoft.com/en-us/cpp/build/reference/mp-build-with-multiple-processes>`_.

For example::

    set CXXFLAGS=/MP4
    python setup.py bdist_wheel

The target level parallelism defines the number of simultaneous ``MSBuild.exe``
processes. It can be set with the ``CMAKE_BUILD_PARALLEL_LEVEL`` environment
variable. To learn more, read `Building Multiple Projects in Parallel with MSBuild
<https://msdn.microsoft.com/en-us/library/bb651793.aspx>`_.

For example::

    set CMAKE_BUILD_PARALLEL_LEVEL=4
    python setup.py bdist_wheel


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


Editable installs
-----------------

.. versionchanged:: 1.0

    Editable installs previously worked without extra configuration.

In-place builds (``python setup.py build_ext --inplace``) work without extra
configuration. Editable installs (``pip install -e .``) require opting in to
scikit-build-core's "inplace" editable mode in ``pyproject.toml``::

    [tool.scikit-build]
    editable.mode = "inplace"


.. _optimized_incremental_build:

Optimized incremental build
---------------------------

To optimize the developer workflow, the CMake build directory is kept inside
the standard setuptools ``build/`` directory (an ``_skbuild`` directory under
``build/temp.*``) and reused across builds.

If a file is added to the CMake build system by updating one of the
``CMakeLists.txt`` files, the generated build-system will automatically
detect the change and reconfigure the project the next time a build is run.


Environment variable configuration
----------------------------------

Scikit-build support environment variables to configure some options. These are:

``CMAKE_ARGS``
  This will add configuration options when configuring CMake.

``CMAKE_GENERATOR``
  This selects the CMake generator to use. See :doc:`/generators`.

In addition, every scikit-build-core setting can be set using a corresponding
``SKBUILD_*`` environment variable. See the `scikit-build-core configuration
documentation <https://scikit-build-core.readthedocs.io/en/latest/configuration/index.html>`__.

.. versionchanged:: 1.0

    The ``SKBUILD_CONFIGURE_OPTIONS`` and ``SKBUILD_BUILD_OPTIONS``
    environment variables were removed; use ``CMAKE_ARGS`` and
    ``CMAKE_BUILD_PARALLEL_LEVEL`` instead.


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
