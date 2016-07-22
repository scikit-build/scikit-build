#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_root_package
----------------------------------

Ensure that skbuild supports the root package, i.e. the nameless top level
"package".
"""

from . import project_setup_py_test


@project_setup_py_test(("unit", "root-package"), ["build"], clear_cache=True)
def test_hello_builds():
    pass
