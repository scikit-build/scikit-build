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
            official_vs_year = "2008"

        # For Python 3.3 to Python 3.4: VS2010
        elif (
            version.major == 3 and (
                version.minor >= 3 and
                version.minor <= 4
            )
        ):
            official_vs_year = "2010"

        # For Python 3.5 and above: VS2015
        elif version.major == 3 and version.minor >= 5:
            official_vs_year = "2015"

        else:
            raise RuntimeError("Only Python >= 2.7 is supported on Windows.")

        assert official_vs_year is not None

        supported_vs_years = [official_vs_year]

        for vs_year in supported_vs_years:
            self.default_generators.extend([
                CMakeVisualStudioCommandLineGenerator("Ninja",
                                                      vs_year),
                CMakeVisualStudioIDEGenerator(vs_year),
                CMakeVisualStudioCommandLineGenerator(
                    "NMake Makefiles", vs_year),
                CMakeVisualStudioCommandLineGenerator(
                    "NMake Makefiles JOM", vs_year)
            ])

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
        super(CMakeVisualStudioIDEGenerator, self).__init__(vs_base)


def _get_msvc_compiler_env(vs_version):
    from setuptools import monkey
    monkey.patch_for_msvc_specialized_compiler()
    arch = "x86"
    if vs_version < 14:
        if platform.architecture()[0] == "64bit":
            arch = "amd64"
        try:
            import distutils.msvc9compiler
            return distutils.msvc9compiler.query_vcvarsall(vs_version, arch)
        except ImportError:
            print("failed to import 'distutils.msvc9compiler'")
    else:
        if platform.architecture()[0] == "64bit":
            arch = "x86_amd64"
        try:
            import distutils._msvccompiler
            vc_env = distutils._msvccompiler._get_vc_env(arch)
            return {
                'PATH': vc_env.get('path', ''),
                'INCLUDE': vc_env.get('include', ''),
                'LIB': vc_env.get('lib', '')
            }
        except ImportError:
            print("failed to import 'distutils._msvccompiler'")
    return {}


class CMakeVisualStudioCommandLineGenerator(CMakeGenerator):
    def __init__(self, name, year):
        vc_env = _get_msvc_compiler_env(VS_YEAR_TO_VERSION[year])
        env = {str(key.upper()): str(value) for key, value in vc_env.items()}
        super(CMakeVisualStudioCommandLineGenerator, self).__init__(name, env)
