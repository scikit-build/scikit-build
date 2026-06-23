=======
Hacking
=======

Where the build backend lives
-----------------------------

.. versionchanged:: 2.0

    The ``skbuild.cmaker`` module and the rest of the classic build backend
    were removed.

The build backend is provided by the setuptools plugin of `scikit-build-core
<https://scikit-build-core.readthedocs.io>`_; ``skbuild`` is a thin wrapper
around it that re-exports ``setup()`` and ships the scikit-build CMake
modules. If you want to hack on how projects are configured and built, look
at the `scikit-build-core repository
<https://github.com/scikit-build/scikit-build-core>`_.

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
