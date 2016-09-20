"""This module defines object specific to Linux platform."""

from . import unix


class LinuxPlatform(unix.UnixPlatform):
    """Linux implementation of :class:`.abstract.CMakePlatform`"""
    pass
