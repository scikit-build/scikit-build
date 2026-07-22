# scikit-build

[![image](https://github.com/scikit-build/scikit-build/actions/workflows/ci.yml/badge.svg)](https://github.com/scikit-build/scikit-build/actions/workflows/ci.yml)
[![image](https://dev.azure.com/scikit-build/scikit-build/_apis/build/status/scikit-build.scikit-build?branchName=main)](https://dev.azure.com/scikit-build/scikit-build/_build/latest?definitionId=1&branchName=main)
[![Code coverage status](https://codecov.io/gh/scikit-build/scikit-build/branch/main/graph/badge.svg)](https://codecov.io/gh/scikit-build/scikit-build)
[![GitHub Discussion](https://img.shields.io/static/v1?label=Discussions&message=Ask&color=blue&logo=github)](https://github.com/orgs/scikit-build/discussions)

<!-- START-INTRO -->

**scikit-build** is a Python build system for CPython C/C++/Fortran/Cython extensions using CMake.

The scikit-build package is fundamentally just glue between the `setuptools` Python module and [CMake](https://cmake.org).

The next generation of scikit-build, [scikit-build-core](https://scikit-build-core.readthedocs.io), provides a simple, reliable build backend for CMake that does not use setuptools and provides a lot of new features. Since scikit-build 1.0, scikit-build (classic) is a thin wrapper around scikit-build-core's setuptools plugin. If you do not require setuptools, you should consider using scikit-build-core directly instead. This package only adds the legacy CMake helper modules (which have modern equivalents) and the compatibility `setup()` wrapper.

To get started, see [this example](https://scikit-build.readthedocs.io/en/latest/usage.html#example-of-setup-py-cmakelists-txt-and-pyproject-toml). For more examples, see [scikit-build-sample-projects](https://github.com/scikit-build/scikit-build-sample-projects).

## Quick upgrade instructions for 1.0

Code should build (using standards-based tools, like `pip`/`uv`/`build`/`cibuildwheel`) as long as you are not using our internals. `setup.py` commands may not work (a few do, like `setup.py build_ext --inplace`, which works better than before). You can now use `tool.scikit-build`, as described by scikit-build-core.

If you keep `from skbuild import setup` in `setup.py`, require scikit-build and use scikit-build-core's setuptools backend for auto-cmake/ninja and config-settings support:

```toml
[build-system]
requires = ["scikit-build>=1"]
build-backend = "scikit_build_core.setuptools.build_meta"
```

If you want to use scikit-build-core directly but keep setuptools:

```toml
[build-system]
requires = ["scikit-build-core[setuptools]>=1"]
build-backend = "scikit_build_core.setuptools.build_meta"
```

And either use setup with at least a `cmake_source_dir` argument:

```python
from setuptools import setup

setup(cmake_source_dir=".")
```

or the following in your pyproject.toml:

```toml
[tool.scikit-build]
cmake.source-dir = "."
```

Either one of those will cause scikit-build-core's setuptools plugin to activate. The defaults for the native plugin are different from the `skbuild.setup()` wrapper (`scikit_build_core.setuptools.wrapper.setup()`); for example `SKBUILD_CONFIGURE_OPTIONS`/`SKBUILD_BUILD_OPTIONS` are not adapted without the wrapper.

And if you want to use the native, non-setuptools backend:

```toml
[build-system]
requires = ["scikit-build-core>=1"]
build-backend = "scikit_build_core.build"
```

You'll need to use a `project` table and `tool.scikit-build`; `setup.py`, `MANIFEST.in`, and `setup.cfg` have no effect without setuptools. The native backend is recommended unless you specifically need a setuptools or hatchling plugin, e.g. to combine with other plugins.

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

PyCMake was created at SciPy 2014 in response to general difficulties building C++ and Fortran based Python extensions across platforms. It was renamed to "scikit-build" in 2016. Scikit-build-core was started in 2022, and became the backend for this package in 2026.

## New backend

- All deprecated setuptools/distutils features are removed in scikit-build 1.0, like the `test` command, `easy_install`, etc. Use standards-based development instead, like `uv`, `pip`, `build`, etc.
- Older versions of CMake (\<3.15) are no longer supported.

## Miscellaneous

- Free software: MIT license
- Documentation: <http://scikit-build.readthedocs.org>
- Source code: <https://github.com/scikit-build/scikit-build>
- Discussions: <https://github.com/orgs/scikit-build/discussions>
- Scikit-build-core: <https://github.com/scikit-build/scikit-build-core>

Support for this work was provided by NSF grant [OAC-2209877](https://www.nsf.gov/awardsearch/showAward?AWD_ID=2209877).
