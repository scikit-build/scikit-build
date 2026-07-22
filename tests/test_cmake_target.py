"""test_cmake_target
----------------------------------

Builds the `test-cmake-target` sample project, which uses the
`cmake_install_target` keyword to install only the "runtime" component
through a custom install target.
"""

from __future__ import annotations

from . import cmake_build_dir


def test_cmake_install_target(project_setup_py_test):
    with project_setup_py_test("test-cmake-target", ["build"]) as project_dir:
        build_dir = cmake_build_dir(project_dir)
        assert build_dir is not None
        installed = {path.name for path in (build_dir / "cmake-install").rglob("*") if path.is_file()}
        assert "runtime.txt" in installed
        assert "foo.txt" not in installed
