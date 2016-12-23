# -*- coding: utf-8 -*-
"""
scikit-build is an improved build system generator for CPython C extensions.

This module provides the *glue* between the setuptools Python module and CMake.
"""

from .setuptools_wrap import setup  # noqa: F401

__author__ = 'The scikit-build team'
__email__ = 'scikit-build@googlegroups.com'
__version__ = '0.5.1'

__all__ = ["setup"]
