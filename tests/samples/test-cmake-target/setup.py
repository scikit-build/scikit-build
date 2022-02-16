from skbuild import setup

setup(
    name="test-cmake-target",
    version="1.2.3",
    description="a minimal example package using a non-default target",
    author="The scikit-build team",
    license="MIT",
    cmake_install_target="install-runtime",
)
