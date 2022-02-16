from skbuild import setup

setup(
    name="test_include_exclude_data",
    version="0.1.0",
    cmake_languages=(),
    packages=["hello", "hello2"],
    include_package_data=True,
    exclude_package_data={
        "": [
            "*/*/*_data4_include_from_manifest_and_exclude_from_setup.txt",
            "*/*/*_data4_cmake_generated_and_exclude_from_setup.txt",
        ]
    },
)
