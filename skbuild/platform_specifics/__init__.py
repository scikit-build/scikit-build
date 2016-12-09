"""This package provides :func:`get_platform()` allowing to get an instance
of :class:`.abstract.CMakePlatform` matching the current platform.
"""

from .abstract import CMakeGenerator  # noqa: F401
from .platform_factory import get_platform   # noqa: F401

__all__ = ["CMakeGenerator", "get_platform"]
