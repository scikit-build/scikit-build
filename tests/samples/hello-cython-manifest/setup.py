from skbuild import setup

setup(
    name="hello-cython-manifest",
    version="1.2.3",
    description="a minimal example package (cython version) with package data",
    author="The scikit-build team",
    license="MIT",
    packages=["hello_cython_manifest"],
    # The extra '/' was *only* added to check that scikit-build can handle it.
    package_dir={"hello_cython_manifest": "hello/"},
    include_package_data=True,
)
