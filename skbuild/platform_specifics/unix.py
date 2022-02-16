"""This module defines object specific to Unix platform."""

import os

from . import abstract
from .abstract import CMakeGenerator


# pylint:disable=abstract-method
class UnixPlatform(abstract.CMakePlatform):
    """Unix implementation of :class:`.abstract.CMakePlatform`."""

    def __init__(self):
        super(UnixPlatform, self).__init__()
        try:
            import ninja  # pylint: disable=import-outside-toplevel

            ninja_executable_path = os.path.join(ninja.BIN_DIR, "ninja")
            ninja_args = ["-DCMAKE_MAKE_PROGRAM:FILEPATH=" + ninja_executable_path]
        except ImportError:
            ninja_args = []

        self.default_generators = [CMakeGenerator("Ninja", args=ninja_args), CMakeGenerator("Unix Makefiles")]
