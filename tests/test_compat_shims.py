"""test_compat_shims
----------------------------------

Tests for the ``skbuild.constants`` and ``skbuild.cmaker`` compatibility
shims kept for downstream ``setup.py`` files.
"""

from __future__ import annotations

import glob
import importlib
import os
import pathlib
import re
import subprocess
import sys
import textwrap
import warnings

import pytest

from . import get_ext_suffix


def import_shim(name):
    """Import a shim module without tripping ``filterwarnings = error``."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        return importlib.import_module(name)


@pytest.mark.parametrize("module", ["skbuild.constants", "skbuild.cmaker"])
def test_import_warns(module):
    # Subprocess: the warning only fires on first import, and this process
    # may already have the module cached.
    code = textwrap.dedent(
        f"""
        import warnings

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            import {module}
        messages = [str(w.message) for w in caught if issubclass(w.category, DeprecationWarning)]
        assert any("compatibility shim" in m for m in messages), messages
        """
    )
    subprocess.run([sys.executable, "-c", code], check=True)


def test_skbuild_plat_name():
    constants = import_shim("skbuild.constants")
    plat_name = constants.skbuild_plat_name()
    assert plat_name
    if sys.platform.startswith("darwin"):
        assert re.fullmatch(r"macosx-\d+\.\d+-\S+", plat_name)


def test_get_cmake_version():
    cmaker = import_shim("skbuild.cmaker")
    assert re.match(r"^\d+\.\d+\.\d+", cmaker.get_cmake_version())


def test_get_cmake_version_bad_executable():
    cmaker = import_shim("skbuild.cmaker")
    exceptions = importlib.import_module("skbuild.exceptions")
    with pytest.raises(exceptions.SKBuildError):
        cmaker.get_cmake_version(os.path.join(os.sep, "nonexistent", "cmake"))


def test_cmake_install_dir_shape():
    constants = import_shim("skbuild.constants")
    path = pathlib.PurePath(constants.CMAKE_INSTALL_DIR())
    assert not path.is_absolute()
    assert path.parts[0] == "build"
    assert path.parts[-2:] == ("_skbuild", "cmake-install")


def test_extension_compiles_against_cmake_install(project_setup_py_test):
    # The sample compiles a plain setuptools Extension against a header that
    # CMake installs into CMAKE_INSTALL_DIR() (the DracoPy pattern). Import
    # the shim first so the in-process setup.py import is a cached no-op.
    import_shim("skbuild.constants")
    with project_setup_py_test("test-cmake-install-dir", ["build"]):
        assert glob.glob(f"build/lib.*/hello_cid{get_ext_suffix()}")
