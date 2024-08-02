from __future__ import annotations

from skbuild import setup

setup(
    name="hello",
    version="1.2.3",
    description="a minimal example package (cpp version)",
    author="The scikit-build team",
    license="MIT",
    packages=["hello"],
    setup_requires=[],
    cmake_source_dir="../../",
)
