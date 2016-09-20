"""This module defines object specific to Unix platform."""

from . import abstract


class UnixPlatform(abstract.CMakePlatform):
    """Unix implementation of :class:`.abstract.CMakePlatform`."""

    def __init__(self):
        super(UnixPlatform, self).__init__()
        self.default_generators = ["Unix Makefiles", ]
