#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_cmaker
----------------------------------

Tests for CMaker functionality.
"""

import os
import re

from skbuild.cmaker import CMaker


def test_get_python_version():
    assert re.match(r'^[23](\.?)[0-9]$', CMaker.get_python_version())


def test_get_python_library():
    python_library = CMaker.get_python_library(CMaker.get_python_version())
    assert python_library
    assert os.path.exists(python_library)
