from __future__ import annotations

from skbuild import setup

setup(
    name="hello",
    version="1.2.3",
    description="a minimal example package (CMakeLists not in top-level dir)",
    author="The scikit-build team",
    license="MIT",
    packages=["hello"],
    cmake_source_dir="hello",
)
