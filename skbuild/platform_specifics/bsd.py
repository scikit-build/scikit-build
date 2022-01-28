"""This module defines object specific to BSD platform."""

from . import unix


# pylint:disable=abstract-method
class BSDPlatform(unix.UnixPlatform):
    """BSD implementation of :class:`.abstract.CMakePlatform`."""
