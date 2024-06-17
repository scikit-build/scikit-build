"""This modules implements the logic allowing to instantiate the expected
:class:`.abstract.CMakePlatform`."""

from __future__ import annotations

# pylint: disable=import-outside-toplevel
import platform

from . import abstract


def get_platform() -> abstract.CMakePlatform:
    """Return an instance of :class:`.abstract.CMakePlatform` corresponding
    to the current platform."""
    this_platform = platform.system().lower()

    if this_platform == "windows":
        from . import windows

        return windows.WindowsPlatform()

    # Some flexibility based on what emcripten distros decide to call themselves
    if this_platform.startswith(("linux", "emscripten", "pyodide", "android")):
        from . import linux

        return linux.LinuxPlatform()

    if this_platform.startswith("cygwin"):
        from . import cygwin

        return cygwin.CygwinPlatform()

    if this_platform in ["darwin", "ios"]:
        from . import osx

        return osx.OSXPlatform()

    if this_platform in {"freebsd", "netbsd", "os400", "openbsd"}:
        from . import bsd

        return bsd.BSDPlatform()

    if this_platform == "sunos":
        from . import sunos

        return sunos.SunOSPlatform()

    if this_platform == "aix":
        from . import aix

        return aix.AIXPlatform()

    msg = f"Unsupported platform: {this_platform:s}. Please contact the scikit-build team."
    raise RuntimeError(msg)
