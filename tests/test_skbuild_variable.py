"""test_skbuild_variable
------------------------

Tries to build the `fail-unless-skbuild-set` sample project.  The CMake variable
"SKBUILD" must be set in order for the build to succeed.
"""

from __future__ import annotations

from . import project_setup_py_test


@project_setup_py_test("fail-unless-skbuild-set", ["build"], disable_languages_test=True)
def test_skbuild_variable_builds():
    pass


@project_setup_py_test("fail-unless-skbuild-set", ["sdist"], disable_languages_test=True)
def test_skbuild_variable_sdist():
    pass


@project_setup_py_test("fail-unless-skbuild-set", ["bdist_wheel"], disable_languages_test=True)
def test_skbuild_variable_wheel():
    pass
