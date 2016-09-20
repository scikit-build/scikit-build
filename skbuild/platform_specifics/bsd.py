"""This module defines object specific to BSD platform."""

from . import unix


class BSDPlatform(unix.UnixPlatform):
    """BSD implementation of :class:`.abstract.CMakePlatform`."""
    pass
