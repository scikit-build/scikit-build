"""test_skbuild_variable
------------------------

Tries to build the `fail-unless-skbuild-set` sample project.  The CMake variable
"SKBUILD" must be set in order for the build to succeed.
"""

from __future__ import annotations


def test_skbuild_variable_builds(project_setup_py_test):
    with project_setup_py_test("fail-unless-skbuild-set", ["build"], disable_languages_test=True):
        pass


def test_skbuild_variable_sdist(project_setup_py_test):
    with project_setup_py_test("fail-unless-skbuild-set", ["sdist"], disable_languages_test=True):
        pass


def test_skbuild_variable_wheel(project_setup_py_test):
    with project_setup_py_test("fail-unless-skbuild-set", ["bdist_wheel"], disable_languages_test=True):
        pass
