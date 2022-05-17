"""This module defines object specific to Windows platform."""

from __future__ import print_function

import os
import platform
import re
import subprocess
import sys
import textwrap
from itertools import count

from . import abstract
from .abstract import CMakeGenerator

VS_YEAR_TO_VERSION = {
    "2008": 9,
    "2010": 10,
    "2012": 11,
    "2013": 12,
    "2015": 14,
    "2017": 15,
    "2019": 16,
    "2022": 17,
}
"""Describes the version of `Visual Studio` supported by
:class:`CMakeVisualStudioIDEGenerator` and
:class:`CMakeVisualStudioCommandLineGenerator`.

The different version are identified by their year.
"""

VS_YEAR_TO_MSC_VER = {
    "2008": "1500",  # VS 2008
    "2010": "1600",  # VS 2010
    "2012": "1700",  # VS 2012
    "2013": "1800",  # VS 2012
    "2015": "1900",  # VS 2015
    "2017": "1910",  # VS 2017 - can be +9
    "2019": "1920",  # VS 2019 - can be +9
    "2022": "1930",  # VS 2022 - can be +9
}


class WindowsPlatform(abstract.CMakePlatform):
    """Windows implementation of :class:`.abstract.CMakePlatform`."""

    def __init__(self):
        super(WindowsPlatform, self).__init__()
        self._vs_help = ""
        vs_help_template = (
            textwrap.dedent(
                """
            Building windows wheels for Python {pyver} requires Microsoft Visual Studio %s.
            Get it with "%s":

              %s
            """  # noqa: E501
            )
            .strip()
            .format(pyver="%s.%s" % sys.version_info[:2])
        )

        # For Python 2.7 to Python 3.2: VS2008
        if (2, 7) <= sys.version_info < (3, 3):
            supported_vs_years = [("2008", None)]
            self._vs_help = vs_help_template % (
                supported_vs_years[0][0],
                "Microsoft Visual C++ Compiler for Python 2.7",
                "http://aka.ms/vcpython27",
            )

        # For Python 3.3 to Python 3.4: VS2010
        elif (3, 3) <= sys.version_info < (3, 5):
            supported_vs_years = [("2010", None)]
            self._vs_help = vs_help_template % (
                supported_vs_years[0][0],
                "Windows SDK for Windows 7 and .NET 4.0",
                "https://www.microsoft.com/download/details.aspx?id=8279",
            )

        # For Python 3.5: VS2019, VS2017, VS2015
        elif (3, 5) <= sys.version_info < (3, 6):
            supported_vs_years = [("2019", "v142"), ("2017", "v140"), ("2015", None)]
            self._vs_help = vs_help_template % (
                supported_vs_years[0][0],
                "Visual Studio 2015",
                "https://visualstudio.microsoft.com/vs/older-downloads/",
            )
            self._vs_help += (
                "\n\n"
                + textwrap.dedent(
                    """
                Or with "Visual Studio 2017" or "Visual Studio 2019":

                  https://visualstudio.microsoft.com/vs/
                """
                ).strip()
            )

        # For Python 3.6 and above: VS2022, VS2019, VS2017
        elif (3, 6) <= sys.version_info:
            supported_vs_years = [("2022", "v143"), ("2019", "v142"), ("2017", "v141")]
            self._vs_help = vs_help_template % (
                supported_vs_years[0][0],
                "Visual Studio 2017",
                "https://visualstudio.microsoft.com/vs/",
            )
            self._vs_help += (
                "\n\n"
                + textwrap.dedent(
                    """
                Or with "Visual Studio 2019":

                  https://visualstudio.microsoft.com/vs/

                Or with "Visual Studio 2022":

                  https://visualstudio.microsoft.com/vs/
                """
                ).strip()
            )
        else:
            raise RuntimeError("Only Python >= 2.7 is supported on Windows.")

        try:
            import ninja  # pylint: disable=import-outside-toplevel

            ninja_executable_path = os.path.join(ninja.BIN_DIR, "ninja")
            ninja_args = ["-DCMAKE_MAKE_PROGRAM:FILEPATH=" + ninja_executable_path]
        except ImportError:
            ninja_args = []

        extra = []
        for vs_year, vs_toolset in supported_vs_years:
            vs_version = VS_YEAR_TO_MSC_VER[vs_year]
            args = ["-D_SKBUILD_FORCE_MSVC={}".format(vs_version)]
            self.default_generators.extend(
                [
                    CMakeVisualStudioCommandLineGenerator("Ninja", vs_year, vs_toolset, args=ninja_args + args),
                    CMakeVisualStudioIDEGenerator(vs_year, vs_toolset),
                ]
            )
            extra.append(CMakeVisualStudioCommandLineGenerator("NMake Makefiles", vs_year, vs_toolset, args=args))
        self.default_generators.extend(extra)

    @property
    def generator_installation_help(self):
        """Return message guiding the user for installing a valid toolchain."""
        return self._vs_help


class CMakeVisualStudioIDEGenerator(CMakeGenerator):
    """
    Represents a Visual Studio CMake generator.

    .. automethod:: __init__
    """

    def __init__(self, year, toolset=None):
        """Instantiate a generator object with its name set to the `Visual
        Studio` generator associated with the given ``year``
        (see :data:`VS_YEAR_TO_VERSION`), the current platform (32-bit
        or 64-bit) and the selected ``toolset`` (if applicable).
        """
        vs_version = VS_YEAR_TO_VERSION[year]
        vs_base = "Visual Studio {} {}".format(vs_version, year)
        if platform.machine() == "ARM64":
            vs_arch = "ARM64"
        elif platform.architecture()[0] == "64bit":
            vs_arch = "x64"
        else:
            vs_arch = "Win32"
        super(CMakeVisualStudioIDEGenerator, self).__init__(vs_base, toolset=toolset, arch=vs_arch)


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
        import winreg  # pylint: disable=import-outside-toplevel
    except ImportError:
        # Support Python 2.7
        try:
            import _winreg as winreg  # pylint: disable=import-outside-toplevel
        except ImportError:
            return ""

    # get registry key associated with Visual Studio installations
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"Software\Microsoft\VisualStudio\SxS\VC7",
            0,
            winreg.KEY_READ | winreg.KEY_WOW64_32KEY,
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
        if sys.version_info >= (3, 6):
            extra_args["encoding"] = "utf-8" if sys.platform.startswith("cygwin") else "mbcs"
            extra_args["errors"] = "strict"
        path = subprocess.check_output(
            [
                os.path.join(root, "Microsoft Visual Studio", "Installer", "vswhere.exe"),
                "-version",
                "[{:.1f}, {:.1f})".format(vs_version, vs_version + 1),
                "-prerelease",
                "-requires",
                "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
                "-property",
                "installationPath",
                "-products",
                "*",
            ],
            **extra_args
        ).strip()
        if (3, 0) <= sys.version_info[:2] <= (3, 5):
            path = path.decode()
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

    if 10 <= vs_version <= 14:
        return _find_visual_studio_2010_to_2015(vs_version)

    return ""


# To avoid multiple slow calls to ``subprocess.check_output()`` (either directly or
# indirectly through ``query_vcvarsall``), results of previous calls are cached.
__get_msvc_compiler_env_cache = {}


def _get_msvc_compiler_env(vs_version, vs_toolset=None):
    """
    Return a dictionary of environment variables corresponding to ``vs_version``
    that can be used with  :class:`CMakeVisualStudioCommandLineGenerator`.

    The ``vs_toolset`` is used only for Visual Studio 2017 or newer (``vs_version >= 14``).

    If specified, ``vs_toolset`` is used to set the `-vcvars_ver=XX.Y` argument passed to
    ``vcvarsall.bat`` script.
    """

    # Set architecture
    arch = "x86"
    if platform.machine() == "ARM64":
        arch = "x86_arm64"
    elif platform.architecture()[0] == "64bit":
        if vs_version < 14:
            arch = "amd64"
        else:
            arch = "x86_amd64"

    # If any, return cached version
    cache_key = ",".join([str(vs_version), arch, str(vs_toolset)])
    if cache_key in __get_msvc_compiler_env_cache:
        return __get_msvc_compiler_env_cache[cache_key]

    from setuptools import monkey  # pylint: disable=import-outside-toplevel

    monkey.patch_for_msvc_specialized_compiler()

    if vs_version < 14:
        try:
            import distutils.msvc9compiler  # pylint: disable=import-outside-toplevel

            cached_env = distutils.msvc9compiler.query_vcvarsall(vs_version, arch)
            __get_msvc_compiler_env_cache[cache_key] = cached_env
            return cached_env
        except ImportError:
            print("failed to import 'distutils.msvc9compiler'")
    else:
        vc_dir = find_visual_studio(vs_version)
        vcvarsall = os.path.join(vc_dir, "vcvarsall.bat")
        if not os.path.exists(vcvarsall):
            return {}

        # Set vcvars_ver argument based on toolset
        vcvars_ver = ""
        if vs_toolset is not None and vs_version >= 15:
            match = re.findall(r"^v(\d\d)(\d+)$", vs_toolset)[0]
            if match:
                vcvars_ver = "-vcvars_ver=%s.%s" % match

        try:
            # TODO: should always be shell=True, but currently requires this
            out = subprocess.check_output(
                'cmd /u /c "{}" {} {} && set'.format(vcvarsall, arch, vcvars_ver),
                stderr=subprocess.STDOUT,
                shell=sys.platform.startswith("cygwin"),
            )
            out = out.decode("utf-16le", errors="replace")
            if sys.version_info[0] < 3:
                out = out.encode("utf-8")

            vc_env = {
                key.lower(): value
                for key, _, value in (line.partition("=") for line in out.splitlines())
                if key and value
            }

            cached_env = {
                "PATH": vc_env.get("path", ""),
                "INCLUDE": vc_env.get("include", ""),
                "LIB": vc_env.get("lib", ""),
            }
            __get_msvc_compiler_env_cache[cache_key] = cached_env
            return cached_env
        except subprocess.CalledProcessError as exc:
            print(exc.output)

    return {}


class CMakeVisualStudioCommandLineGenerator(CMakeGenerator):
    """
    Represents a command-line CMake generator initialized with a
    specific `Visual Studio` environment.

    .. automethod:: __init__
    """

    def __init__(self, name, year, toolset=None, args=None):
        """Instantiate CMake command-line generator.

        The generator ``name`` can be values like `Ninja`, `NMake Makefiles`
        or `NMake Makefiles JOM`.

        The ``year`` defines the `Visual Studio` environment associated
        with the generator. See :data:`VS_YEAR_TO_VERSION`.

        If set, the ``toolset`` defines the `Visual Studio Toolset` to select.

        The platform (32-bit or 64-bit) is automatically selected based
        on the value of ``platform.architecture()[0]``.
        """
        vc_env = _get_msvc_compiler_env(VS_YEAR_TO_VERSION[year], toolset)
        env = {str(key.upper()): str(value) for key, value in vc_env.items()}
        super(CMakeVisualStudioCommandLineGenerator, self).__init__(name, env, args=args)
        self._description = "{} ({})".format(self.name, CMakeVisualStudioIDEGenerator(year, toolset).description)
