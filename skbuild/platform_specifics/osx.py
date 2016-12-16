"""This module defines object specific to OSX platform."""

import sys

from . import unix


class OSXPlatform(unix.UnixPlatform):
    """OSX implementation of :class:`.abstract.CMakePlatform`."""

    @property
    def generator_installation_help(self):
        return (
            "Building MacOSX wheels for Python "
            + ("%s.%s" % sys.version_info[:2]) +
            " requires the use of XCode. "
            "Get it here: "
            "https://developer.apple.com/xcode/"
        )
