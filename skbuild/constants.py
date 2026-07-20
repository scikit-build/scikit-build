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

from scikit_build_core.builder.builder import archs_to_tags, get_archs
from scikit_build_core.builder.macos import get_macosx_deployment_target

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

    machine = os.environ.get("CMAKE_OSX_ARCHITECTURES") or ";".join(get_archs(os.environ)) or platform.machine()
    machine = ";".join(archs_to_tags(machine.split(";")))

    target = get_macosx_deployment_target(arm=machine == "arm64")
    return f"macosx-{target}-{machine}"
