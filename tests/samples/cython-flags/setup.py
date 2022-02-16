from skbuild import setup

setup(
    name="cython-flags",
    version="1.2.3",
    description="a minimal example package (cython version)",
    author="The scikit-build team",
    license="MIT",
    packages=["cython_flags"],
    package_dir={"cython_flags": "hello"},
)
