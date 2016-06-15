import sys
import platform

from . import abstract

class WindowsPlatform(abstract.CMakePlatform):

    def __init__(self):
        super(WindowsPlatform, self).__init__()
        self.default_generators = ["MinGW Makefiles", ]
        version = sys.version_info

        # For Python 2.7 to Python 3.2: VS2008
        if (
            (version.major == 2 and version.minor >= 7) or
            (version.major == 3 and version.minor <= 2)
        ):
            vs_base = "Visual Studio 9 2008"

        # For Python 3.3 to Python 3.4: VS2010
        elif (
            version.major == 3 and (
                version.minor >= 3 and
                version.minor <= 4
            )
        ):
            vs_base = "Visual Studio 10 2010"

        # For Python 3.5 and above: VS2015
        elif version.major == 3 and version.minor >= 5:
            vs_base = "Visual Studio 14 2015"

        else:
            raise RuntimeError("Only Python >= 2.7 is supported on Windows.")

        # Python is Win64, build a Win64 module
        if platform.architecture() == "x64":
            vs_base += " Win64"

        # only VS 11 and above support ARM, but include it here in hopes of
        # making future work easier.
        elif platform.architecture() == "ARM":
            vs_base += " ARM"

        # we're implicitly doing nothing for 32-bit builds.  Their generator
        # string IDs seem to be just the vs_base.

        self.default_generators.insert(0, vs_base)

