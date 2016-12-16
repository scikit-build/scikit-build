"""This module defines object specific to Linux platform."""

import platform
import sys

from . import unix


class LinuxPlatform(unix.UnixPlatform):
    """Linux implementation of :class:`.abstract.CMakePlatform`"""

    @property
    def generator_installation_help(self):
        arch = "x64" if platform.architecture()[0] == "64bit" else "x86"
        return (
            "Building Linux wheels for Python "
            + ("%s.%s" % sys.version_info[:2]) +
            " requires a compiler like gcc.\n"
            "\n"
            "Build tools can be installed using your distribution package"
            "manager:\n"
            "  centos: sudo yum groupinstall 'Development Tools'\n"
            "  debian/ubuntu: sudo apt-get install build-essential\n"
            "\n"
            "To build compliant wheel, consider also using a manylinux system."
            "Get it with \"dockcross/manylinux-%s\" docker image: "
            "https://github.com/dockcross/dockcross#readme" % arch
        )
