from __future__ import annotations

import os

from setuptools import Extension

from skbuild import setup
from skbuild.constants import CMAKE_INSTALL_DIR

# Mirrors projects like DracoPy: CMake installs headers/libraries, then a
# plain setuptools Extension compiles against them via CMAKE_INSTALL_DIR().
setup(
    name="hello-cid",
    version="1.2.3",
    description="a minimal example compiling an extension against CMake-installed files",
    author="The scikit-build team",
    license="MIT",
    ext_modules=[
        Extension(
            "hello_cid",
            sources=["hello_cid.c"],
            include_dirs=[os.path.join(CMAKE_INSTALL_DIR(), "include")],
        )
    ],
)
