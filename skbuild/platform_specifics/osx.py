"""This module defines object specific to OSX platform."""

import sys
import textwrap

from . import unix


class OSXPlatform(unix.UnixPlatform):
    """OSX implementation of :class:`.abstract.CMakePlatform`."""

    @property
    def generator_installation_help(self) -> str:
        """Return message guiding the user for installing a valid toolchain."""
        return (
            textwrap.dedent(
                """
            Building MacOSX wheels for Python {pyver} requires XCode.
            Get it here:

              https://developer.apple.com/xcode/
            """
            )
            .format(pyver=".".join(str(v) for v in sys.version_info[:2]))
            .strip()
        )
