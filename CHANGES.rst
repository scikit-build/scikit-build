=============
Release Notes
=============

This is the list of changes to scikit-build between each release. For full
details, see the commit logs at http://github.com/scikit-build/scikit-build

Next Release
============

New features
------------

* Improve user experience by running CMake only if needed. See :issue:`207`

* Add support for :ref:`cmake_with_sdist <cmake_with_sdist>` setup keyword argument.

* Add support for ``--force-cmake`` and ``--skip-cmake`` global :ref:`setup options <setuptools_options>`.

* scikit-build conda-forge recipe added by :user:`isuruf`.
  See `conda-forge/staged-recipes#1989 <https://github.com/conda-forge/staged-recipes/pull/1989>`_

* Add support for `development mode <https://packaging.python.org/distributing/#working-in-development-mode>`_. (:issue:`187`).

Bug fixes
---------

* Fix scikit-build source distribution and add test. See :issue:`214`
  Thanks :user:`isuruf` for reporting the issue.

Documentation
-------------

* add :doc:`/changes` section

* allow github issues and users to easily be referenced using ``:issue:`XY```
  and ``:user:`username``` markups.
  This functionality is enabled by the `sphinx-issue <https://github.com/sloria/sphinx-issues>`_ sphinx extension

* make_a_release: Ensure uploaded distributions are signed

* usage:

 * Add empty cross-compilation / wheels building sections
 * Add "Why should I use scikit-build ?"
 * Add "Setup options" section

Tests
-----

* Improve "push_dir" tests to not rely on build directory name.
  Thanks :user:`isuruf` for reporting the issue.

* travis/install_pyenv: Improve MacOSX build time updating scikit-ci-addons

Cleanups
--------

* appveyor.yml:

 * Remove unused "on_failure: event logging" and "notifications: GitHubPullRequest"
 * Remove unused SKIP env variable


Scikit-build 0.4.0
==================

New features
------------

* Add support for ``--hide-listing`` option

 * allow to build distributions without displaying files being included

 * useful when building large project on Continuous Integration service limiting
   the amount of log produced by the build

* CMake module: ``skbuild/resources/cmake/FindPythonExtensions.cmake``

 * Function ``python_extension_module``: add support for `module suffix <https://github.com/scikit-build/scikit-build/commit/0a9b7ef>`_

Bug fixes
---------

* Do not package python modules under "purelib" dir in non-pure wheel

* CMake module: ``skbuild/resources/cmake/targetLinkLibrariesWithDynamicLookup.cmake``:

 * Fix the logic checking for cross-compilation (the regression
   was introduced by :issue:`51` and :issue:`47`

 * It configure the text project setting `CMAKE_ENABLE_EXPORTS <https://cmake.org/cmake/help/v3.6/prop_tgt/ENABLE_EXPORTS.html?highlight=enable_export>`_ to ON. Doing
   so ensure the executable compiled in the test exports symbols (if supported
   by the underlying platform)

Docs
----

* Add `short note <http://scikit-build.readthedocs.io/en/latest/cmake-modules.html>`_
  explaining how to include scikit-build CMake module
* Move "Controlling CMake using scikit-build" into a "hacking" section
* Add initial version of `"extension_build_system" documentation <http://scikit-build.readthedocs.io/en/latest/extension_build_system.html>`_

Tests
-----

* tests/samples: Simplify project removing unneeded install rules and file copy

* Simplify continuous integration

 * use `scikit-ci <http://scikit-ci.readthedocs.io/en/latest/>`_ and
   `scikit-ci-addons <http://scikit-ci-addons.readthedocs.io/en/latest/>`_
 * speed up build setting up caching

* Makefile:

 * Fix `coverage` target
 * Add `docs-only` target allowing to regenerate the Sphinx documentation
   without opening a new page in the browser.

Scikit-build 0.3.0
==================

New features
------------

* Improve support for "pure", "CMake" and "hybrid" python package

 * a "pure" package is a python package that have all files living
   in the project source tree

 * an "hybrid" package is a python package that have some files living
   in the project source tree and some files installed by CMake

 * a "CMake" package is a python package that is fully generated and
   installed by CMake without any of his files existing in the source
   tree

* Add support for source distribution. See :issue:`84`

* Add support for setup arguments specific to scikit-build:

 * ``cmake_args``: additional option passed to CMake
 * ``cmake_install_dir``: relative directory where the CMake project being
   built should be installed
 * ``cmake_source_dir``: location of the CMake project

* Add CMake module ``FindNumPy.cmake``

* Automatically set ``package_dir`` to reasonable defaults

* Support building project without CMakeLists.txt



Bug fixes
---------

* Fix dispatch of arguments to setuptools, CMake and build tool. See :issue:`118`

* Force binary wheel generation. See :issue:`106`

* Fix support for ``py_modules`` (`6716723 <https://github.com/scikit-build/scikit-build/commit/6716723>`_)

* Do not raise error if calling "clean" command twice

Documentation
-------------

* Improvement of documentation published
  on http://scikit-build.readthedocs.io/en/latest/

* Add docstrings for most of the modules, classes and functions

Tests
-----

* Ensure each test run in a dedicated temporary directory

* Add tests to raise coverage from 70% to 91%

* Refactor CI testing infrastructure introducing CI drivers written in python
  for AppVeyor, CircleCI and TravisCI

* Switch from ``nose`` to ``py.test``

* Relocate sample projects into a dedicated
  home: https://github.com/scikit-build/scikit-build-sample-projects

Cleanups
--------

* Refactor commands introducing ``set_build_base_mixin`` and ``new_style``

* Remove unused code