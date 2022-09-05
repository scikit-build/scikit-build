"""This package provides :func:`get_platform()` allowing to get an instance
of :class:`.abstract.CMakePlatform` matching the current platform.

This folder contains files the define CMake's defaults for given platforms.  Any of them can be overridden by either
command line or by environment variables.
"""

from .abstract import CMakeGenerator  # noqa: F401
from .platform_factory import get_platform  # noqa: F401

__all__ = ["CMakeGenerator", "get_platform"]
