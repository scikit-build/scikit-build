from . import windows
from . import linux
from . import osx

import platform


def get_platform():
    this_platform = platform.system()
    if this_platform == "Linux":
        return linux.LinuxPlatform()
    elif this_platform == "Windows":
        return windows.WindowsPlatform()
    elif this_platform == "Darwin" :
        return osx.OSXPlatform()
    else:
        raise RuntimeError("Unsupported platform: {:s}. Please contact "
                           "the PyCMake team.".format(this_platform))
