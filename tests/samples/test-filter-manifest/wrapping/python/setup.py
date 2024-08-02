from __future__ import annotations

from skbuild import setup


def exclude_dev_files(cmake_manifest):
    return list(filter(lambda name: not name.endswith((".a", ".h")), cmake_manifest))


setup(
    name="hello",
    version="1.2.3",
    description="a minimal example package (cpp version)",
    author="The scikit-build team",
    license="MIT",
    packages=["hello"],
    setup_requires=[],
    cmake_source_dir="../../",
    cmake_process_manifest_hook=exclude_dev_files,
)
