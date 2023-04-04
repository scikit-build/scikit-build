"""This module defines object specific to Linux platform."""

from __future__ import annotations

import platform
import sys
import textwrap

import distro

from . import unix


class LinuxPlatform(unix.UnixPlatform):
    """Linux implementation of :class:`.abstract.CMakePlatform`"""

    @staticmethod
    def build_essential_install_cmd() -> tuple[str, str]:
        """Return a tuple of the form ``(distribution_name, cmd)``.

        ``cmd`` is the command allowing to install the build tools
        in the current Linux distribution. It set to an empty string
        if the command is not known.

        ``distribution_name`` is the name of the current distribution. It
        is set to an empty string if the distribution could not be
        determined.
        """
        # gentoo, slackware: Compiler is available by default.

        distribution_name = distro.id()
        cmd = ""
        if distribution_name in {"debian", "Ubuntu", "mandrake", "mandriva"}:
            cmd = "sudo apt-get install build-essential"

        elif distribution_name in {"centos", "fedora", "redhat", "turbolinux", "yellowdog", "rocks"}:
            # http://unix.stackexchange.com/questions/16422/cant-install-build-essential-on-centos#32439
            cmd = "sudo yum groupinstall 'Development Tools'"

        elif distribution_name in {"SuSE"}:
            # http://serverfault.com/questions/437680/equivalent-development-build-tools-for-suse-professional-11#437681
            cmd = "zypper install -t pattern devel_C_C++"

        return distribution_name, cmd

    @property
    def generator_installation_help(self) -> str:
        """Return message guiding the user for installing a valid toolchain."""
        distribution_name, cmd = self.build_essential_install_cmd()
        install_help = ""
        if distribution_name:
            install_help = f"But scikit-build does *NOT* know how to install it on {distribution_name}\n"
        if distribution_name and cmd:
            install_help = f"It can be installed using {distribution_name} package manager:\n\n  {cmd}\n"

        arch = "x64" if platform.architecture()[0] == "64bit" else "x86"
        version_str = ".".join(str(v) for v in sys.version_info[:2])
        return textwrap.dedent(
            f"""
            Building Linux wheels for Python {version_str} requires a compiler (e.g gcc).
            {install_help}
            To build compliant wheels, consider using the manylinux system described in PEP-513.
            Get it with "dockcross/manylinux-{arch}" docker image:

              https://github.com/dockcross/dockcross#readme

            For more details, please refer to scikit-build documentation:

              http://scikit-build.readthedocs.io/en/latest/generators.html#linux
            """
        ).strip()
