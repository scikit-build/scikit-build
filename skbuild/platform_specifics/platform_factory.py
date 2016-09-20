"""This modules implements the logic allowing to instantiate the expected
:class:`.abstract.CMakePlatform`."""

import platform

from . import bsd
from . import linux
from . import osx
from . import windows


def get_platform():
    """Return an instance of :class:`.abstract.CMakePlatform` corresponding
    to the current platform."""
    this_platform = platform.system().lower()

    if this_platform == "windows":
        return windows.WindowsPlatform()
    if this_platform == "linux":
        return linux.LinuxPlatform()
    elif this_platform == "freebsd":
        return bsd.BSDPlatform()
    elif this_platform == "darwin":
        return osx.OSXPlatform()
    else:
        raise RuntimeError("Unsupported platform: {:s}. Please contact "
                           "the scikit-build team.".format(this_platform))
