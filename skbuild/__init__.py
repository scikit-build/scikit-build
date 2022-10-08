"""
scikit-build is an improved build system generator for CPython C extensions.

This module provides the *glue* between the setuptools Python module and CMake.
"""

from typing import List

from ._version import version as __version__
from .setuptools_wrap import setup

__author__ = "The scikit-build team"
__email__ = "scikit-build@googlegroups.com"

__all__ = ["setup", "__version__"]


# Cleaner Python 3.7 command line completion
def __dir__() -> List[str]:
    return __all__
