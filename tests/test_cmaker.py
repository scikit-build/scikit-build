#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_cmaker
----------------------------------

Tests for CMaker functionality.
"""

import os
import pytest
import re

from skbuild.cmaker import (CMAKE_BUILD_DIR, CMaker)
from skbuild.exceptions import SKBuildError
from skbuild.utils import push_dir

from . import _tmpdir


def test_get_python_version():
    assert re.match(r'^[23](\.?)[0-9]$', CMaker.get_python_version())


def test_get_python_library():
    python_library = CMaker.get_python_library(CMaker.get_python_version())
    assert python_library
    assert os.path.exists(python_library)


def test_make_without_build_dir_fails():
    src_dir = _tmpdir('test_make_without_build_dir_fails')
    with push_dir(str(src_dir)), pytest.raises(SKBuildError) as excinfo:
        CMaker().make()
    assert "Did you forget to run configure before make" in str(excinfo.value)


def test_make_without_configure_fails(capfd):
    src_dir = _tmpdir('test_make_without_configure_fails')
    src_dir.ensure(CMAKE_BUILD_DIR, dir=1)
    with push_dir(str(src_dir)), pytest.raises(SKBuildError) as excinfo:
        CMaker().make()
    _, err = capfd.readouterr()
    assert "An error occurred while building with CMake." in str(excinfo.value)
    assert "Error: could not load cache" in err
