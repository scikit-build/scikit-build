"""Tests for the deprecation warnings emitted ahead of the scikit-build-core
backend swap. These deprecated features become errors, are ignored, or are
removed when scikit-build-core's setuptools plugin takes over.

The suite globally ignores ``SKBuildDeprecationWarning`` (see ``pyproject.toml``),
so these tests assert the warnings explicitly via ``pytest.warns`` / a subprocess.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

import skbuild
from skbuild.exceptions import SKBuildDeprecationWarning

# Deprecated internal modules removed by the scikit-build-core backend.
DEPRECATED_MODULES = [
    "cmaker",
    "constants",
    "utils",
    "command",
    "platform_specifics",
    "setuptools_wrap",
]

# Deprecated setup() keyword arguments: (kwargs, substring of the message).
DEPRECATED_KWARGS = [
    ({"cmake_with_sdist": True}, "cmake_with_sdist"),
    ({"cmake_install_target": "custom"}, "cmake_install_target"),
    ({"cmake_languages": ("C", "Fortran")}, "cmake_languages"),
    ({"cmake_minimum_required_version": "3.20"}, "cmake_minimum_required_version"),
]


@pytest.mark.parametrize("module", DEPRECATED_MODULES)
def test_internal_module_import_warns(module):
    # Module objects are cached, so re-importing in-process would not re-run the
    # warning. Use a fresh interpreter that turns the warning into an error.
    code = (
        "import warnings\n"
        "from skbuild.exceptions import SKBuildDeprecationWarning\n"
        "warnings.simplefilter('error', SKBuildDeprecationWarning)\n"
        f"import skbuild.{module}\n"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=False)
    assert result.returncode != 0, f"importing skbuild.{module} did not warn:\n{result.stderr}"
    assert "SKBuildDeprecationWarning" in result.stderr
    assert f"skbuild.{module} is deprecated" in result.stderr


def test_import_skbuild_setup_is_not_deprecated():
    # The documented happy path must stay warning-free.
    code = (
        "import warnings\n"
        "from skbuild.exceptions import SKBuildDeprecationWarning\n"
        "warnings.simplefilter('error', SKBuildDeprecationWarning)\n"
        "from skbuild import setup\n"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(("kwargs", "match"), DEPRECATED_KWARGS)
def test_deprecated_setup_keyword_warns(kwargs, match, monkeypatch, tmp_path):
    # "--name" is a display-only command, so setup() emits the deprecation and
    # returns without configuring CMake (the tmp dir has no CMakeLists.txt).
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["setup.py", "--name"])
    with pytest.warns(SKBuildDeprecationWarning, match=match):
        skbuild.setup(name="dep", version="1.0", **kwargs)


def test_default_setup_keywords_do_not_warn(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["setup.py", "--name"])
    import warnings

    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        skbuild.setup(name="dep", version="1.0")
    assert not [w for w in recorded if issubclass(w.category, SKBuildDeprecationWarning)]
