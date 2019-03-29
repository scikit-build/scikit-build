"""This module defines object specific to Windows platform."""

from __future__ import print_function

import os
import platform
import subprocess
import sys
import textwrap

from itertools import count

from .abstract import CMakeGenerator

from . import abstract


class WindowsPlatform(abstract.CMakePlatform):
    """Windows implementation of :class:`.abstract.CMakePlatform`."""

    def __init__(self):
        super(WindowsPlatform, self).__init__()
        version = sys.version_info
        self._vs_help = ""
        vs_help_template = textwrap.dedent(
            """
            Building windows wheels for Python {pyver} requires Microsoft Visual Studio %s.
            Get it with "%s":

              %s
            """  # noqa: E501
        ).strip().format(pyver="%s.%s" % sys.version_info[:2])

        # For Python 2.7 to Python 3.2: VS2008
        if (
            (version.major == 2 and version.minor >= 7) or
            (version.major == 3 and version.minor <= 2)
        ):
            official_vs_year = "2008"
            self._vs_help = vs_help_template % (
                official_vs_year,
                "Microsoft Visual C++ Compiler for Python 2.7",
                "http://aka.ms/vcpython27"
            )

        # For Python 3.3 to Python 3.4: VS2010
        elif (
            version.major == 3 and (
                version.minor >= 3 and
                version.minor <= 4
            )
        ):
            official_vs_year = "2010"
            self._vs_help = vs_help_template % (
                official_vs_year,
                "Windows SDK for Windows 7 and .NET 4.0",
                "https://www.microsoft.com/download/details.aspx?id=8279"
            )
            #

        # For Python 3.5 and above: VS2015
        elif version.major == 3 and version.minor >= 5:
            official_vs_year = "2015"
            self._vs_help = vs_help_template % (
                official_vs_year,
                "Microsoft Visual C++ Build Tools",
                "http://landinghub.visualstudio.com/visual-cpp-build-tools"
            )
            self._vs_help += "\n\n" + textwrap.dedent(
                """
                Or with "Visual Studio 2015":

                  https://visualstudio.com/
                """
            ).strip()

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

    @property
    def generator_installation_help(self):
        """Return message guiding the user for installing a valid toolchain."""
        return self._vs_help


VS_YEAR_TO_VERSION = {
    "2008": 9,
    "2010": 10,
    "2012": 11,
    "2013": 12,
    "2015": 14,
    "2017": 15
}
"""Describes the version of `Visual Studio` supported by
:class:`CMakeVisualStudioIDEGenerator` and
:class:`CMakeVisualStudioCommandLineGenerator`.

The different version are identified by their year.
"""


class CMakeVisualStudioIDEGenerator(CMakeGenerator):
    """
    Represents a Visual Studio CMake generator.

    .. automethod:: __init__
    """
    def __init__(self, year):
        """Instantiate a generator object with its name set to the `Visual
        Studio` generator associated with the given ``year``
        (see :data:`VS_YEAR_TO_VERSION`) and the current platform (32-bit
        or 64-bit).
        """
        vs_version = VS_YEAR_TO_VERSION[year]
        vs_base = "Visual Studio %s %s" % (vs_version, year)
        # Python is Win64, build a Win64 module
        if platform.architecture()[0] == "64bit":
            vs_base += " Win64"
        super(CMakeVisualStudioIDEGenerator, self).__init__(vs_base)


def _find_visual_studio_2010_to_2015(vs_version):
    """Adapted from https://github.com/python/cpython/blob/3.5/Lib/distutils/_msvccompiler.py

    The ``vs_version`` corresponds to the `Visual Studio` version to lookup.
    See :data:`VS_YEAR_TO_VERSION`.

    Return Visual Studio installation path found by looking up all key/value pairs
    associated with the ``Software\\Microsoft\\VisualStudio\\SxS\\VC7`` registry key.
    If no install is found, returns an empty string.

    Each key/value pair is the visual studio version (e.g `14.0`) and the installation
    path (e.g `C:/Program Files (x86)/Microsoft Visual Studio 14.0/VC/`).
    """
    # winreg module
    try:
        import winreg
    except ImportError:
        # Support Python 2.7
        try:
            import _winreg as winreg
        except ImportError:
            return ""

    # get registry key associated with Visual Studio installations
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"Software\Microsoft\VisualStudio\SxS\VC7",
            0,
            winreg.KEY_READ | winreg.KEY_WOW64_32KEY
        )
    except OSError:
        return ""

    with key:
        for i in count():
            try:
                v, vc_dir, vt = winreg.EnumValue(key, i)
            except OSError:
                break
            # winreg.REG_SZ means "A null-terminated string"
            if v and vt == winreg.REG_SZ and os.path.isdir(vc_dir):
                try:
                    version = int(float(v))
                except (ValueError, TypeError):
                    continue
                if version == vs_version:
                    return vc_dir
    return ""


def _find_visual_studio_2017_or_newer(vs_version):
    """Adapted from https://github.com/python/cpython/blob/3.7/Lib/distutils/_msvccompiler.py

    The ``vs_version`` corresponds to the `Visual Studio` version to lookup.
    See :data:`VS_YEAR_TO_VERSION`.

    Returns `path` based on the result of invoking ``vswhere.exe``.
    If no install is found, returns an empty string.

    ..note:

        If ``vswhere.exe`` is not available, by definition, VS 2017 or newer is not installed.
    """
    root = os.environ.get("ProgramFiles(x86)") or os.environ.get("ProgramFiles")
    if not root:
        return ""

    try:
        extra_args = {}
        if sys.version_info[:3] >= (3, 6, 0):
            extra_args = {'encoding': 'mbcs', 'errors': 'strict'}
        path = subprocess.check_output([
            os.path.join(root, "Microsoft Visual Studio", "Installer", "vswhere.exe"),
            "-version", "[%.1f, %.1f)" % (vs_version, vs_version + 1),
            "-prerelease",
            "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
            "-property", "installationPath",
            "-products", "*",
        ], **extra_args).strip()
    except (subprocess.CalledProcessError, OSError, UnicodeDecodeError):
        return ""

    path = os.path.join(path, "VC", "Auxiliary", "Build")
    if os.path.isdir(path):
        return path

    return ""


def find_visual_studio(vs_version):
    """Return Visual Studio installation path associated with ``vs_version`` or an empty string if any.

    The ``vs_version`` corresponds to the `Visual Studio` version to lookup.
    See :data:`VS_YEAR_TO_VERSION`.

    .. note::

        - For VS 2017 and newer, returns `path` based on the result of invoking ``vswhere.exe``.

        - For VS 2010 to VS 2015, returns `path` by looking up all key/value pairs
          associated with the ``Software\\Microsoft\\VisualStudio\\SxS\\VC7`` registry key. Each
          key/value pair is the visual studio version (e.g `14.0`) and the installation
          path (e.g `C:/Program Files (x86)/Microsoft Visual Studio 14.0/VC/`).

    """
    if 15 <= vs_version:
        return _find_visual_studio_2017_or_newer(vs_version)
    elif 10 <= vs_version <= 14:
        return _find_visual_studio_2010_to_2015(vs_version)
    else:
        return ""


# To avoid multiple slow calls to ``query_vcvarsall`` or ``_get_vc_env``, results
# of previous calls are cached.
__get_msvc_compiler_env_cache = dict()


def _get_msvc_compiler_env(vs_version):
    # pylint:disable=global-statement
    global __get_msvc_compiler_env_cache
    from setuptools import monkey
    monkey.patch_for_msvc_specialized_compiler()
    arch = "x86"
    if vs_version < 14:
        if platform.architecture()[0] == "64bit":
            arch = "amd64"
        # If any, return cached version
        cache_key = ",".join([str(vs_version), arch])
        if cache_key in __get_msvc_compiler_env_cache:
            return __get_msvc_compiler_env_cache[cache_key]
        try:
            import distutils.msvc9compiler
            cached_env = distutils.msvc9compiler.query_vcvarsall(vs_version, arch)
            __get_msvc_compiler_env_cache[cache_key] = cached_env
            return cached_env
        except ImportError:
            print("failed to import 'distutils.msvc9compiler'")
    else:
        if platform.architecture()[0] == "64bit":
            arch = "x86_amd64"
        # If any, return cached version
        cache_key = ",".join([str(vs_version), arch])
        if cache_key in __get_msvc_compiler_env_cache:
            return __get_msvc_compiler_env_cache[cache_key]
        try:
            import distutils._msvccompiler
            from distutils.errors import DistutilsPlatformError
            # pylint:disable=protected-access
            vc_env = distutils._msvccompiler._get_vc_env(arch)
            cached_env = {
                'PATH': vc_env.get('path', ''),
                'INCLUDE': vc_env.get('include', ''),
                'LIB': vc_env.get('lib', '')
            }
            __get_msvc_compiler_env_cache[cache_key] = cached_env
            return cached_env
        except ImportError:
            print("failed to import 'distutils._msvccompiler'")
        except DistutilsPlatformError:
            pass
    return {}


class CMakeVisualStudioCommandLineGenerator(CMakeGenerator):
    """
    Represents a command-line CMake generator initialized with a
    specific `Visual Studio` environment.

    .. automethod:: __init__
    """
    def __init__(self, name, year):
        """Instantiate CMake command-line generator.

        The generator ``name`` can be values like `Ninja`, `NMake Makefiles`
        or `NMake Makefiles JOM`.

        The ``year`` defines the `Visual Studio` environment associated
        with the generator. See :data:`VS_YEAR_TO_VERSION`.

        The platform (32-bit or 64-bit) is automatically selected based
        on the value of ``platform.architecture()[0]``.
        """
        vc_env = _get_msvc_compiler_env(VS_YEAR_TO_VERSION[year])
        env = {str(key.upper()): str(value) for key, value in vc_env.items()}
        super(CMakeVisualStudioCommandLineGenerator, self).__init__(name, env)
