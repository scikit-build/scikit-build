"""This modules implements the logic allowing to instantiate the expected
:class:`.abstract.CMakePlatform`."""

import platform


def get_platform():
    """Return an instance of :class:`.abstract.CMakePlatform` corresponding
    to the current platform."""
    this_platform = platform.system().lower()

    if this_platform == "windows":
        from . import windows
        return windows.WindowsPlatform()

    elif this_platform == "linux":
        from . import linux
        return linux.LinuxPlatform()

    elif this_platform == "freebsd":
        from . import bsd
        return bsd.BSDPlatform()

    elif this_platform == "darwin":
        from . import osx
        return osx.OSXPlatform()

    elif this_platform == "os400":
        from . import bsd
        return bsd.BSDPlatform()

    else:
        raise RuntimeError("Unsupported platform: {:s}. Please contact "
                           "the scikit-build team.".format(this_platform))
