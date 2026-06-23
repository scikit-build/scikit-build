# scikit-build

[![image](https://github.com/scikit-build/scikit-build/actions/workflows/ci.yml/badge.svg)](https://github.com/scikit-build/scikit-build/actions/workflows/ci.yml)

[![image](https://dev.azure.com/scikit-build/scikit-build/_apis/build/status/scikit-build.scikit-build?branchName=main)](https://dev.azure.com/scikit-build/scikit-build/_build/latest?definitionId=1&branchName=main)

[![Code coverage status](https://codecov.io/gh/scikit-build/scikit-build/branch/main/graph/badge.svg)](https://codecov.io/gh/scikit-build/scikit-build)

[![GitHub Discussion](https://img.shields.io/static/v1?label=Discussions&message=Ask&color=blue&logo=github)](https://github.com/orgs/scikit-build/discussions)

<!-- START-INTRO -->

**scikit-build** is a Python build system for CPython C/C++/Fortran/Cython extensions using CMake.

The scikit-build package is fundamentally just glue between the `setuptools` Python module and [CMake](https://cmake.org).

The next generation of scikit-build, [scikit-build-core](https://scikit-build-core.readthedocs.io), is currently under development. This provides a simple, reliable build backend for CMake that does not use setuptools and provides a lot of new features. Scikit-build-core can also power a setuptools-based extension system, which will eventually become the backend for scikit-build (classic). If you do not require extensive customization of the build process, you should consider trying scikit-build-core instead of scikit-build.

To get started, see [this example](https://scikit-build.readthedocs.io/en/latest/usage.html#example-of-setup-py-cmakelists-txt-and-pyproject-toml). For more examples, see [scikit-build-sample-projects](https://github.com/scikit-build/scikit-build-sample-projects).

<!-- END-INTRO -->

## Latest Release

| Versions | Downloads |
|----|----|
| [![image](https://img.shields.io/pypi/v/scikit-build.svg)](https://pypi.python.org/pypi/scikit-build) | [![image](https://img.shields.io/pypi/dm/scikit-build)](https://pypi.python.org/pypi/scikit-build) |
| [![image](https://anaconda.org/conda-forge/scikit-build/badges/version.svg)](https://anaconda.org/conda-forge/scikit-build) | [![image](https://anaconda.org/conda-forge/scikit-build/badges/downloads.svg)](https://anaconda.org/conda-forge/scikit-build) |

<!-- INJECT-CHANGELOG -->

## Publications

Please use the first citation when referencing scikit-build in scientific publications.

- Jean-Christophe Fillion-Robin, Matt McCormick, Omar Padron, Max Smolens, Michael Grauer, & Michael Sarahan. (2018, July 13). jcfr/scipy_2018_scikit-build_talk: SciPy 2018 Talk \| scikit-build: A Build System Generator for CPython C/C++/Fortran/Cython Extensions. Zenodo. <https://doi.org/10.5281/zenodo.2565368>
- Schreiner, Henry, Rickerby, Joe, Grosse-Kunstleve, Ralf, Jakob, Wenzel, Darbois, Matthieu, Gokaslan, Aaron, Fillion-Robin, Jean-Christophe, & McCormick, Matt. (2022, August 1). Building Binary Extensions with pybind11, scikit-build, and cibuildwheel. <https://doi.org/10.25080/majora-212e5952-033>

## History

PyCMake was created at SciPy 2014 in response to general difficulties building C++ and Fortran based Python extensions across platforms. It was renamed to "scikit-build" in 2016. Scikit-build-core was started in 2022.

## Known Issues

These issues are likely to be addressed in upcoming releases, and are already addressed in [scikit-build-core](https://scikit-build-core.readthedocs.io).

- Editable installs do not work with the latest versions of Setuptools (and had issues with older versions, too).
- Configuration scikit-build cares about *must* be specified in `setup()` currently.
- The cache directory (`_skbuild`) may need to be deleted between builds in some cases (like rebuilding with a different Python interpreter).
- AIX requires a newer version of CMake than the IBM-supplied CMake 3.22.0 from the AIX Toolbox for Open Source Software. We currently recommend building CMake from source on AIX.

We are also working on improving scikit-build, so there are some upcoming changes and deprecations:

- All deprecated setuptools/distutils features are also deprecated in scikit-build, like the `test` command, `easy_install`, etc.
- Older versions of CMake (\<3.15) are not recommended; a future version will remove support for older CMake's (along with providing a better mechanism for ensuring a proper CMake is available).

If you need any of these features, please open or find an issue explaining what and why you need something.

## Miscellaneous

- Free software: MIT license
- Documentation: <http://scikit-build.readthedocs.org>
- Source code: <https://github.com/scikit-build/scikit-build>
- Discussions: <https://github.com/orgs/scikit-build/discussions>
- Scikit-build-core: <https://github.com/scikit-build/scikit-build-core>

Support for this work was provided by NSF grant [OAC-2209877](https://www.nsf.gov/awardsearch/showAward?AWD_ID=2209877).
