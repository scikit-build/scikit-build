"""This module defines object specific to Windows platform."""

from __future__ import annotations

import os
import platform
import re
import subprocess
import sys
import textwrap
from typing import Iterable

from setuptools import monkey

from .._compat.typing import TypedDict
from . import abstract
from .abstract import CMakeGenerator

VS_YEAR_TO_VERSION = {
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
    "2017": "1910",  # VS 2017 - can be +9
    "2019": "1920",  # VS 2019 - can be +9
    "2022": "1930",  # VS 2022 - can be +19
}

ARCH_TO_MSVC_ARCH = {
    "Win32": "x86",
    "ARM64": "x86_arm64",
    "x64": "x86_amd64",
}


class CachedEnv(TypedDict):
    """Stored environment."""

    PATH: str
    INCLUDE: str
    LIB: str


class WindowsPlatform(abstract.CMakePlatform):
    """Windows implementation of :class:`.abstract.CMakePlatform`."""

    def __init__(self) -> None:
        super().__init__()
        self._vs_help = textwrap.dedent(
            """
            Building windows wheels requires Microsoft Visual Studio.
            Get it from:
n
             https://visualstudio.microsoft.com/vs/
            """
        ).strip()

        # For Python 3.7 and above: VS2022, VS2019, VS2017
        supported_vs_years = [("2022", "v144"), ("2022", "v143"), ("2019", "v142"), ("2017", "v141")]

        try:
            import ninja  # pylint: disable=import-outside-toplevel

            ninja_executable_path = os.path.join(ninja.BIN_DIR, "ninja")
            ninja_args = [f"-DCMAKE_MAKE_PROGRAM:FILEPATH={ninja_executable_path}"]
        except ImportError:
            ninja_args = []

        extra = []
        for vs_year, vs_toolset in supported_vs_years:
            vs_version = VS_YEAR_TO_MSC_VER[vs_year]
            args = [f"-D_SKBUILD_FORCE_MSVC={vs_version}"]
            self.default_generators.extend(
                [
                    CMakeVisualStudioCommandLineGenerator("Ninja", vs_year, vs_toolset, args=ninja_args + args),
                    CMakeVisualStudioIDEGenerator(vs_year, vs_toolset),
                ]
            )
            extra.append(CMakeVisualStudioCommandLineGenerator("NMake Makefiles", vs_year, vs_toolset, args=args))
        self.default_generators.extend(extra)

    @property
    def generator_installation_help(self) -> str:
        """Return message guiding the user for installing a valid toolchain."""
        return self._vs_help


def _compute_arch() -> str:
    """Currently only supports Intel -> ARM cross-compilation."""
    if platform.machine() == "ARM64" or "arm64" in os.environ.get("SETUPTOOLS_EXT_SUFFIX", "").lower():
        return "ARM64"
    if platform.architecture()[0] == "64bit":
        return "x64"
    return "Win32"


class CMakeVisualStudioIDEGenerator(CMakeGenerator):
    """
    Represents a Visual Studio CMake generator.

    .. automethod:: __init__
    """

    def __init__(self, year: str, toolset: str | None = None) -> None:
        """Instantiate a generator object with its name set to the `Visual
        Studio` generator associated with the given ``year``
        (see :data:`VS_YEAR_TO_VERSION`), the current platform (32-bit
        or 64-bit) and the selected ``toolset`` (if applicable).
        """
        vs_version = VS_YEAR_TO_VERSION[year]
        vs_base = f"Visual Studio {vs_version} {year}"
        vs_arch = _compute_arch()
        super().__init__(vs_base, toolset=toolset, arch=vs_arch)


def _find_visual_studio_2017_or_newer(vs_version: int) -> str:
    """Adapted from https://github.com/python/cpython/blob/3.7/Lib/distutils/_msvccompiler.py

    The ``vs_version`` corresponds to the `Visual Studio` version to lookup.
    See :data:`VS_YEAR_TO_VERSION`.

    Returns `path` based on the result of invoking ``vswhere.exe``.
    If no install is found, returns an empty string.

    ..note:

        If ``vswhere.exe`` is not available, by definition, VS 2017 or newer is not installed.
    """
    root = os.environ.get("PROGRAMFILES(X86)") or os.environ.get("PROGRAMFILES")
    if not root:
        return ""

    try:
        # vswhere.exe may return multiple locations separated by new line. For
        # example for 2022 Build Tools and for 2022 Community Edition. Ideally
        # we want user to have the option to choose, but as a quick fix we just
        # return first available option.
        path = (
            subprocess.run(
                [
                    os.path.join(root, "Microsoft Visual Studio", "Installer", "vswhere.exe"),
                    "-version",
                    f"[{vs_version:.1f}, {vs_version + 1:.1f})",
                    "-prerelease",
                    "-requires",
                    "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
                    "-property",
                    "installationPath",
                    "-products",
                    "*",
                ],
                encoding="utf-8" if sys.platform.startswith("cygwin") else "mbcs",
                check=True,
                stdout=subprocess.PIPE,
                errors="strict",
            )
            .stdout.strip()
            .split("\n")[0]
            .strip()
        )
    except (subprocess.CalledProcessError, OSError, UnicodeDecodeError):
        return ""

    path = os.path.join(path, "VC", "Auxiliary", "Build")
    if os.path.isdir(path):
        return path

    return ""


def find_visual_studio(vs_version: int) -> str:
    """Return Visual Studio installation path associated with ``vs_version`` or an empty string if any.

    The ``vs_version`` corresponds to the `Visual Studio` version to lookup.
    See :data:`VS_YEAR_TO_VERSION`.

    .. note::

        - Returns `path` based on the result of invoking ``vswhere.exe``.

    """
    return _find_visual_studio_2017_or_newer(vs_version)


# To avoid multiple slow calls to ``subprocess.run()`` (either directly or
# indirectly through ``query_vcvarsall``), results of previous calls are cached.
__get_msvc_compiler_env_cache: dict[str, CachedEnv] = {}


def _get_msvc_compiler_env(vs_version: int, vs_toolset: str | None = None) -> CachedEnv | dict[str, str]:
    """
    Return a dictionary of environment variables corresponding to ``vs_version``
    that can be used with  :class:`CMakeVisualStudioCommandLineGenerator`.

    The ``vs_toolset`` is used only for Visual Studio 2017 or newer (``vs_version >= 15``).

    If specified, ``vs_toolset`` is used to set the `-vcvars_ver=XX.Y` argument passed to
    ``vcvarsall.bat`` script.
    """

    # Set architecture
    vc_arch = ARCH_TO_MSVC_ARCH[_compute_arch()]

    # If any, return cached version
    cache_key = ",".join([str(vs_version), vc_arch, str(vs_toolset)])
    if cache_key in __get_msvc_compiler_env_cache:
        return __get_msvc_compiler_env_cache[cache_key]

    if hasattr(monkey, "patch_for_msvc_specialized_compiler"):
        monkey.patch_for_msvc_specialized_compiler()  # type: ignore[no-untyped-call]

    vc_dir = find_visual_studio(vs_version)
    vcvarsall = os.path.join(vc_dir, "vcvarsall.bat")
    if not os.path.exists(vcvarsall):
        return {}

    # Set vcvars_ver argument based on toolset
    vcvars_ver = ""
    if vs_toolset is not None:
        match = re.findall(r"^v(\d\d)(\d+)$", vs_toolset)[0]
        if match:
            match_str = ".".join(match)
            vcvars_ver = f"-vcvars_ver={match_str}"

    try:
        out_bytes = subprocess.run(
            f'cmd /u /c "{vcvarsall}" {vc_arch} {vcvars_ver} && set',
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=sys.platform.startswith("cygwin"),
            check=True,
        ).stdout
        out = out_bytes.decode("utf-16le", errors="replace")

        vc_env = {
            key.lower(): value for key, _, value in (line.partition("=") for line in out.splitlines()) if key and value
        }

        cached_env: CachedEnv = {
            "PATH": vc_env.get("path", ""),
            "INCLUDE": vc_env.get("include", ""),
            "LIB": vc_env.get("lib", ""),
        }
        __get_msvc_compiler_env_cache[cache_key] = cached_env
        return cached_env
    except subprocess.CalledProcessError as exc:
        print(exc.output.decode("utf-16le", errors="replace"), file=sys.stderr, flush=True)

    return {}


class CMakeVisualStudioCommandLineGenerator(CMakeGenerator):
    """
    Represents a command-line CMake generator initialized with a
    specific `Visual Studio` environment.

    .. automethod:: __init__
    """

    def __init__(self, name: str, year: str, toolset: str | None = None, args: Iterable[str] | None = None):
        """Instantiate CMake command-line generator.

        The generator ``name`` can be values like `Ninja`, `NMake Makefiles`
        or `NMake Makefiles JOM`.

        The ``year`` defines the `Visual Studio` environment associated
        with the generator. See :data:`VS_YEAR_TO_VERSION`.

        If set, the ``toolset`` defines the `Visual Studio Toolset` to select.

        The platform (32-bit or 64-bit or ARM) is automatically selected.
        """
        arch = _compute_arch()
        vc_env = _get_msvc_compiler_env(VS_YEAR_TO_VERSION[year], toolset)
        env = {str(key.upper()): str(value) for key, value in vc_env.items()}
        super().__init__(name, env, arch=arch, args=args)
        self._description = f"{self.name} ({CMakeVisualStudioIDEGenerator(year, toolset).description})"
