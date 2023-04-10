from __future__ import annotations

from skbuild import setup

setup(
    name="test_include_exclude_data_with_base",
    version="0.1.0",
    cmake_languages=(),
    packages=["hello", "hello2", "hello.data.subdata", "hello2.data2.subdata2"],
    package_dir={"": "src"},
    include_package_data=True,
    exclude_package_data={
        "hello.data.subdata": [
            "*_data4_cmake_generated_and_exclude_from_setup.txt",
            "*data4_include_from_manifest_and_exclude_from_setup.txt",
        ],
        "hello2.data2.subdata2": [
            "*_data4_cmake_generated_and_exclude_from_setup.txt",
            "*_data4_include_from_manifest_and_exclude_from_setup.txt",
        ],
    },
)
