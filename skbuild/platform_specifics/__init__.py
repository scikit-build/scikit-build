"""This module provides :func:`get_platform()` allowing to get an instance
of :class:`.abstract.CMakePlatform` matching the current platform.
"""

from .platform_factory import get_platform   # noqa: F401

__all__ = ["get_platform"]
