"""This module defines object specific to Windows platform."""

import sys
import platform

from .abstract import CMakeGenerator

from . import abstract


class WindowsPlatform(abstract.CMakePlatform):
    """Windows implementation of :class:`.abstract.CMakePlatform`."""

    def __init__(self):
        super(WindowsPlatform, self).__init__()
        version = sys.version_info

        # For Python 2.7 to Python 3.2: VS2008
        if (
            (version.major == 2 and version.minor >= 7) or
            (version.major == 3 and version.minor <= 2)
        ):
            self.default_generators.append(
                CMakeVisualStudioIDEGenerator("2008")
            )

        # For Python 3.3 to Python 3.4: VS2010
        elif (
            version.major == 3 and (
                version.minor >= 3 and
                version.minor <= 4
            )
        ):
            self.default_generators.append(
                CMakeVisualStudioIDEGenerator("2010")
            )

        # For Python 3.5 and above: VS2015
        elif version.major == 3 and version.minor >= 5:
            self.default_generators.append(
                CMakeVisualStudioIDEGenerator("2015")
            )

        else:
            raise RuntimeError("Only Python >= 2.7 is supported on Windows.")

        self.default_generators.append(
            CMakeGenerator("MinGW Makefiles")
        )


VS_YEAR_TO_VERSION = {
    "2008": 9,
    "2010": 10,
    "2015": 14
}


class CMakeVisualStudioIDEGenerator(CMakeGenerator):
    """
    Represents a Visual Studio CMake generator.

    .. automethod:: __init__
    """
    def __init__(self, year):
        """Instantiate a generator object with its name set to the `Visual
        Studio` generator associated with the given ``year`` and
        the current platform (32-bit or 64-bit).
        """
        vs_version = VS_YEAR_TO_VERSION[year]
        vs_base = "Visual Studio %s %s" % (vs_version, year)
        # Python is Win64, build a Win64 module
        if platform.architecture()[0] == "64bit":
            vs_base += " Win64"
        self._generator_name = vs_base
