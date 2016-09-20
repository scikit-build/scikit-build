"""This module defines object specific to OSX platform."""

from . import unix


class OSXPlatform(unix.UnixPlatform):
    """OSX implementation of :class:`.abstract.CMakePlatform`."""
    pass
