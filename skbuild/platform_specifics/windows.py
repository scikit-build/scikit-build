import sys
import platform

# base class functionality
from . import abstract


class WindowsPlatform(abstract.CMakePlatform):

    def __init__(self):
        super(WindowsPlatform, self).__init__()
        self.default_generators = ["MSYS Makefiles", "MinGW Makefiles"]
        python_major_version = sys.version_info[0]
        # python 3 from the mothership uses VS 2010
        if python_major_version == 3:
            vs_base = "Visual Studio 10"
        # python 2 from the mothership uses VS 2008
        elif python_major_version == 2:
            vs_base = "Visual Studio 9 2008"
        else:
            raise RuntimeError("Only Python 2 and 3 are supported - "
                               "please add support in platform_specific "
                               "scikit-build folder")

        # Python is Win64, build a Win64 module
        if platform.architecture() == "x64":
            vs_base += " Win64"
        # only VS 11 and above support ARM, but include it here in hopes of
        # making future work easier.
        elif platform.architecture() == "ARM":
            vs_base += " ARM"
        # we're implicitly doing nothing for 32-bit builds.  Their generator
        # string IDs seem to be just the vs_base.
        self.default_generators.append(vs_base)
