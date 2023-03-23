from __future__ import annotations

from skbuild import setup

setup(
    name="hello-cython",
    version="1.2.3",
    description="a minimal example package (cython version)",
    author="The scikit-build team",
    license="MIT",
    packages=["hello_cython"],
    # The extra '/' was *only* added to check that scikit-build can handle it.
    package_dir={"hello_cython": "hello/"},
)
