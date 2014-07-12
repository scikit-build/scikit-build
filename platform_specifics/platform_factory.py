import linux
import osx
import windows

import platform

def get_platform():
    this_platform = platform.system()
    if this_platform == "Linux":
        return linux.LinuxPlatform()
    elif this_platform == "Windows":
        return windows.WindowsPlatform()
    elif this_platform == "OSX":
        return osx.OSXPlatform()
    else:
        raise RuntimeError("Unsupported platform: {:s}.  Please contact the PyCMake team.".format(this_platform))