from __future__ import annotations

from setuptools import Extension

from skbuild import setup

setup(
    name="hello",
    version="1.2.3",
    description="a minimal example package",
    author="The scikit-build team",
    license="MIT",
    packages=["hello"],
    ext_modules=[
        Extension(
            "hello._hello_ext",
            sources=["hello/_hello_ext.cxx"],
        )
    ],
)
