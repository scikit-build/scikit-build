"""
Compatibility shim for ``skbuild.constants``.

scikit-build 1.0 builds on scikit-build-core and no longer implements this
module. Only :func:`skbuild_plat_name` is kept, since it is a pure helper that
some downstream ``setup.py`` files use to derive a wheel platform tag. The
classic path helpers (``CMAKE_INSTALL_DIR`` and friends) are intentionally not
provided: they described the old ``_skbuild/`` layout, which scikit-build-core
does not build into.
"""

from __future__ import annotations

import os
import platform
import sys
import warnings
from sysconfig import get_platform

__all__ = ["skbuild_plat_name"]

warnings.warn(
    "skbuild.constants is a compatibility shim for scikit-build <1.0; port to scikit-build-core APIs.",
    DeprecationWarning,
    stacklevel=2,
)


def skbuild_plat_name() -> str:
    """Platform name, e.g. ``macosx-11.0-arm64``, ``linux-x86_64``, ``win-amd64``."""
    if not sys.platform.startswith("darwin"):
        return get_platform()

    supported_macos_architectures = {"x86_64", "arm64"}
    macos_universal2_architectures = {"x86_64", "arm64"}

    release = platform.mac_ver()[0]
    machine = platform.machine()

    release = os.environ.get("MACOSX_DEPLOYMENT_TARGET", "") or release
    major_macos, minor_macos = [*release.split("."), "0"][:2]

    if int(major_macos) >= 11:
        minor_macos = "0"

    archflags = os.environ.get("ARCHFLAGS")
    if archflags is not None:
        machine = ";".join(sorted(set(archflags.split()) & supported_macos_architectures))

    machine = os.environ.get("CMAKE_OSX_ARCHITECTURES", machine)

    if set(machine.split(";")) == macos_universal2_architectures:
        machine = "universal2"

    return f"macosx-{major_macos}.{minor_macos}-{machine}"
