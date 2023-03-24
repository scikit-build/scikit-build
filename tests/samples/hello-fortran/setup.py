from __future__ import annotations

from skbuild import setup

setup(
    name="hello-fortran",
    version="1.2.3",
    description="a minimal example package (fortran version)",
    author="The scikit-build team",
    license="MIT",
    packages=["hello", "bonjour"],
    # package_dir={"hello_fortran": "hello"},
    cmake_languages=("C", "Fortran"),
    cmake_minimum_required_version="3.5",
)
