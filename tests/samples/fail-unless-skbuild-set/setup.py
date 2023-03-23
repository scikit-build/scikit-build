from __future__ import annotations

from skbuild import setup

setup(
    name="fail_unless_skbuild_set",
    version="0.0.1",
    description=('test project that should fail unless the CMake variable "SKBUILD" is set'),
    author="The scikit-build team",
    license="MIT",
)
