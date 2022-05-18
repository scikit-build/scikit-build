"""This modules implements the logic allowing to instantiate the expected
:class:`.abstract.CMakePlatform`."""

# pylint: disable=import-outside-toplevel

import platform


def get_platform():
    """Return an instance of :class:`.abstract.CMakePlatform` corresponding
    to the current platform."""
    this_platform = platform.system().lower()

    if this_platform == "windows":
        from . import windows

        return windows.WindowsPlatform()

    if this_platform == "linux":
        from . import linux

        return linux.LinuxPlatform()

    if this_platform.startswith("cygwin"):
        from . import cygwin

        return cygwin.CygwinPlatform()

    if this_platform == "darwin":
        from . import osx

        return osx.OSXPlatform()

    if this_platform in {"freebsd", "os400", "openbsd"}:
        from . import bsd

        return bsd.BSDPlatform()

    msg = "Unsupported platform: {:s}. Please contact the scikit-build team.".format(this_platform)
    raise RuntimeError(msg)
