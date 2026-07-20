"""
Compatibility shim for ``skbuild.constants``.

scikit-build 1.0 builds on scikit-build-core and no longer implements this
module. Two helpers downstream ``setup.py`` files use are kept:
:func:`skbuild_plat_name` (derives a wheel platform tag) and
:func:`CMAKE_INSTALL_DIR` (points at the CMake install staging directory, so a
plain ``setuptools.Extension`` can compile against CMake-installed headers and
libraries). The other classic path helpers (``CMAKE_BUILD_DIR``,
``SKBUILD_DIR``, and friends) described the old ``_skbuild/`` layout and are
not provided.
"""

from __future__ import annotations

import os
import platform
import sys
import warnings
from sysconfig import get_platform

from setuptools import Distribution
from scikit_build_core.builder.builder import archs_to_tags, get_archs
from scikit_build_core.builder.macos import get_macosx_deployment_target

__all__ = ["CMAKE_INSTALL_DIR", "skbuild_plat_name"]

warnings.warn(
    "skbuild.constants is a compatibility shim for scikit-build <1.0; port to scikit-build-core APIs.",
    DeprecationWarning,
    stacklevel=2,
)


def CMAKE_INSTALL_DIR() -> str:
    """Directory where CMake installs files before setuptools merges them into
    the wheel.

    scikit-build-core's setuptools backend stages the CMake install under
    setuptools' ``build_temp`` and runs CMake before compiling plain
    ``setuptools.Extension`` modules, as classic scikit-build did. Limits:
    command-line overrides such as ``--build-temp`` are not visible here, and
    editable installs do not populate this directory.
    """
    build_ext = Distribution().get_command_obj("build_ext")
    assert build_ext is not None
    build_ext.ensure_finalized()
    build_temp = build_ext.build_temp
    assert build_temp is not None
    return os.path.join(build_temp, "_skbuild", "cmake-install")


def skbuild_plat_name() -> str:
    """Platform name, e.g. ``macosx-11.0-arm64``, ``linux-x86_64``, ``win-amd64``."""
    if not sys.platform.startswith("darwin"):
        return get_platform()

    machine = os.environ.get("CMAKE_OSX_ARCHITECTURES") or ";".join(get_archs(os.environ)) or platform.machine()
    machine = ";".join(archs_to_tags(machine.split(";")))

    target = get_macosx_deployment_target(arm=machine == "arm64")
    return f"macosx-{target}-{machine}"
