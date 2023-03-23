from __future__ import annotations

from skbuild import setup

setup(
    name="fail_with_fatal_error_cmakelists",
    version="0.0.1",
    description=(
        "test project that should always fail to build because it provides a CMakeLists.txt reporting a FATAL_ERROR"
    ),
    author="The scikit-build team",
    license="MIT",
)
