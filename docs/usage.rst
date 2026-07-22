
.. _why:

===============================
Why should I use scikit-build ?
===============================

Scikit-build is a replacement for `setuptools.Extension
<https://setuptools.pypa.io/en/latest/userguide/ext_modules.html>`_ that
builds extension modules with CMake, providing:

- better support for :doc:`additional compilers and build systems </generators>`
- first-class :ref:`cross-compilation <cross_compilation>` support
- location of dependencies and their associated build requirements

Scikit-build is a lightweight wrapper around the setuptools plugin of
`scikit-build-core <https://scikit-build-core.readthedocs.io>`_. Use it when
you have an existing ``setup.py``-based project or need setuptools features;
for new projects, use scikit-build-core directly.

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
- The classic ``build-system`` table:
  ``requires = ["setuptools", "scikit-build", "cmake", "ninja"]`` with
  ``build-backend = "setuptools.build_meta"``. The recommended backend is now
  ``scikit_build_core.setuptools.build_meta``, which adds ``cmake`` and
  ``ninja`` only when needed and supports config-settings; see
  :ref:`basic_usage_example`.

The following changes are breaking:

- All scikit-build-specific command line options were removed:
  ``--build-type``, ``-G``/``--generator``, ``-j N``, ``--cmake-executable``,
  ``--skip-generator-test``, ``--hide-listing``, ``--force-cmake``,
  ``--skip-cmake``, ``--install-target``, as well as the
  ``setup.py <setuptools args> -- <cmake args> -- <build tool args>``
  triple-section syntax. Use the ``CMAKE_ARGS`` and ``CMAKE_GENERATOR``
  environment variables, the ``cmake_args`` keyword of ``setup()``, or
  scikit-build-core's ``[tool.scikit-build]`` settings in ``pyproject.toml``
  (or the equivalent ``SKBUILD_*`` environment variables or config-settings)
  instead. See the `scikit-build-core configuration documentation
  <https://scikit-build-core.readthedocs.io/en/latest/configuration/index.html>`__.

- ``cmake_with_sdist=True`` now raises an error. ``cmake_languages`` and
  ``cmake_minimum_required_version`` are accepted but ignored with a warning;
  the minimum CMake version is configured with the ``cmake.version`` setting
  in the ``[tool.scikit-build]`` table of ``pyproject.toml``.

- The internal Python API is gone; only ``skbuild.setup`` and
  ``skbuild.exceptions.SKBuildError`` remain public.
  ``skbuild.command.*`` and ``skbuild.platform_specifics`` were removed.
  ``skbuild.cmaker``, ``skbuild.constants``, ``skbuild.utils`` and
  ``skbuild.setuptools_wrap`` remain importable as deprecated shims that
  warn on import: ``skbuild.cmaker`` keeps only ``get_cmake_version()``,
  ``skbuild.constants`` keeps only ``CMAKE_INSTALL_DIR()`` and
  ``skbuild_plat_name()``, and the last two expose nothing.
  ``skbuild.exceptions.SKBuildError`` is now an alias of setuptools'
  ``SetupError``, so it is no longer a ``RuntimeError``; its
  ``SKBuildInvalidFileInstallationError`` and
  ``SKBuildGeneratorNotFoundError`` subclasses were removed.

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

Make a folder named ``my_project`` as your project root folder, and place the
following in your project's ``setup.py`` file::

    from skbuild import setup  # This line replaces 'from setuptools import setup'
    setup(
        name="hello-cpp",
        version="1.2.3",
        description="a minimal example package (cpp version)",
        author='The scikit-build team',
        license="MIT",
        packages=['hello'],
        python_requires=">=3.10",
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

Then, add a ``pyproject.toml`` declaring the build backend::

    [build-system]
    requires = ["scikit-build>=1"]
    build-backend = "scikit_build_core.setuptools.build_meta"

The ``scikit_build_core.setuptools.build_meta`` backend adds ``cmake`` (and
``ninja``) to the build requirements only when a suitable version is not
already available, and supports config-settings (see
:ref:`usage-setuptools_options`). If you don't want those, you can use the
standard setuptools backend here; then list ``cmake`` (and ``ninja``) in
``requires`` yourself.

Make a hello folder inside my_project folder and place `_hello.cxx <https://github.com/scikit-build/scikit-build-sample-projects/blob/8fdbc8a0dd78656ea0b431e005b49f3e19786444/projects/hello-cpp/hello/_hello.cxx>`_ and `__init__.py <https://github.com/scikit-build/scikit-build-sample-projects/blob/8fdbc8a0dd78656ea0b431e005b49f3e19786444/projects/hello-cpp/hello/__init__.py>`_ inside hello folder.

Now everything is ready; go to my_project's parent folder and type the following command to install your extension::

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

.. versionchanged:: 1.0

    scikit-build no longer intercepts or rewrites setuptools options.

Standard setuptools options are handled by setuptools itself and can be
declared in ``setup.py``, ``setup.cfg``, or the ``[project]`` table of
``pyproject.toml`` as usual. See the `setuptools documentation
<https://setuptools.pypa.io/en/latest/userguide/>`_.

scikit-build options
^^^^^^^^^^^^^^^^^^^^

Scikit-build augments the ``setup()`` function with the following options:

- ``cmake_args``: List of `CMake options <https://cmake.org/cmake/help/latest/manual/cmake.1.html#options>`_.

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

These options are described in more detail in the `scikit-build-core
setuptools plugin documentation
<https://scikit-build-core.readthedocs.io/en/latest/plugins/setuptools.html>`__.
All other scikit-build-core settings can be set in the ``[tool.scikit-build]``
table of ``pyproject.toml``; see the `scikit-build-core configuration
documentation
<https://scikit-build-core.readthedocs.io/en/latest/configuration/index.html>`__.

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

Build with a standard frontend like ``pip``, ``build`` or ``uv``. When using
the ``scikit_build_core.setuptools.build_meta`` backend (see
:ref:`basic_usage_example`), any scikit-build-core setting can be passed as a
config-setting::

    pip install . -C cmake.build-type=Debug
    python -m build -C cmake.args="-DSOME_FEATURE:BOOL=OFF"

CMake options can also be passed using the ``CMAKE_ARGS`` environment
variable, the ``cmake_args`` keyword of ``setup()``, or scikit-build-core's
``[tool.scikit-build]`` settings in ``pyproject.toml``.


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

.. _usage_enabling_parallel_build:

Parallel builds
---------------

The build runs through ``cmake --build``; with the ``Ninja`` generator it is
parallel by default. Set the `CMAKE_BUILD_PARALLEL_LEVEL
<https://cmake.org/cmake/help/latest/envvar/CMAKE_BUILD_PARALLEL_LEVEL.html>`_
environment variable to control the number of parallel jobs::

    CMAKE_BUILD_PARALLEL_LEVEL=3 pip install .


.. _support_isolated_build:

Support for isolated build
--------------------------

Build frontends like ``pip`` and ``build`` install the
``build-system.requires`` entries from ``pyproject.toml`` into an isolated
environment before building. scikit-build supports isolated builds, as well
as builds with isolation disabled (``pip install --no-build-isolation``).


Editable installs
-----------------

.. versionchanged:: 1.0

    Editable installs previously worked without extra configuration.

In-place builds (``python setup.py build_ext --inplace``) work without extra
configuration. Editable installs (``pip install -e .``) require opting in to
scikit-build-core's "inplace" editable mode in ``pyproject.toml``::

    [tool.scikit-build]
    editable.mode = "inplace"

For details, including setuptools' strict editable mode, see the
`scikit-build-core setuptools plugin documentation
<https://scikit-build-core.readthedocs.io/en/latest/plugins/setuptools.html#editable-installs>`__.


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

``SKBUILD_CONFIGURE_OPTIONS``
  Extra arguments appended when configuring CMake, like ``CMAKE_ARGS``. (Deprecated)

``SKBUILD_BUILD_OPTIONS``
  Extra arguments forwarded to ``cmake --build``. (Deprecated)

Both ``SKBUILD_*_OPTIONS`` variables are split following shell quoting rules
and only honored when building through ``skbuild.setup()``.

In addition, every scikit-build-core setting can be set using a corresponding
``SKBUILD_*`` environment variable. See the `scikit-build-core configuration
documentation <https://scikit-build-core.readthedocs.io/en/latest/configuration/index.html>`__.


.. _cross_compilation:

Cross-compilation
-----------------

Cross-compilation works through the standard CMake mechanisms (`CMake
toolchains
<https://cmake.org/cmake/help/latest/manual/cmake-toolchains.7.html>`_). See
the scikit-build-core `cross-compilation guide
<https://scikit-build-core.readthedocs.io/en/latest/guide/crosscompile.html>`_;
tools like `cibuildwheel <https://cibuildwheel.pypa.io>`_ handle the common
macOS and Windows cases automatically.
