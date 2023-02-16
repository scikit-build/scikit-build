"""This package provides :func:`get_platform()` allowing to get an instance
of :class:`.abstract.CMakePlatform` matching the current platform.

This folder contains files the define CMake's defaults for given platforms.  Any of them can be overridden by either
command line or by environment variables.
"""

from __future__ import annotations

from .abstract import CMakeGenerator
from .platform_factory import get_platform

__all__ = ["CMakeGenerator", "get_platform"]
