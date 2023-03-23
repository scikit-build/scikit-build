from __future__ import annotations

from skbuild import setup

setup(
    name="fail_outside_project_root",
    version="0.0.1",
    description=(
        "test project that should always fail to build because it "
        "tries to CMake-install something outside of its root"
    ),
    author="The scikit-build team",
    license="MIT",
)
