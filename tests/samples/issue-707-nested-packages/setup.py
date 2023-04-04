from __future__ import annotations

from skbuild import setup

setup(
    name="hello-nested",
    version="1.2.3",
    description="Nested packages with a single CMakeLists.txt",
    author="The scikit-build team",
    license="MIT",
    packages=["hello_nested", "hello_nested.goodbye_nested"],
    python_requires=">=3.7",
)
