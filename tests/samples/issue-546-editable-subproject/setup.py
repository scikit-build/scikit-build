from __future__ import print_function

import pybind11

from skbuild import setup

pybind11_path = pybind11.get_cmake_dir()


setup(
    name="pkg",
    version="0.0.1",
    packages=["pkg", "pkg.subpkg"],
    package_dir={"": "src"},
    cmake_install_dir="src/pkg",
    cmake_args=["-Dpybind11_SEARCH_PATH={}".format(pybind11_path)],
)
