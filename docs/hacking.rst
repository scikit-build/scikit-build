=======
Hacking
=======

Where the build backend lives
-----------------------------

.. versionchanged:: 1.0

    The classic build backend was removed; a few internal modules survive as
    deprecated shims.

The build backend is provided by the setuptools plugin of `scikit-build-core
<https://scikit-build-core.readthedocs.io>`_; ``skbuild`` is a thin wrapper
around it that re-exports ``setup()`` and ships the scikit-build CMake
modules. If you want to hack on how projects are configured and built, look
at the `scikit-build-core repository
<https://github.com/scikit-build/scikit-build-core>`_.

The public Python API is ``skbuild.setup`` and
``skbuild.exceptions.SKBuildError``. Anything else is deprecated:
``skbuild.cmaker``, ``skbuild.constants``, ``skbuild.utils`` and
``skbuild.setuptools_wrap`` are compatibility shims that warn on import and
keep only the handful of helpers downstream ``setup.py`` files use (see
below).

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
