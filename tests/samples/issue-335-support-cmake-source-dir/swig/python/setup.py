
from skbuild import setup

setup(
    name="my_proj",
    version="0.1",
    description="a minimal example package (cpp version)",
    author='The scikit-build team',
    license="MIT",
    packages=['my_proj'],
    tests_require=[],
    setup_requires=[],
    cmake_args=['-DPYTHON_REL_SITE_ARCH:PATH=my_proj'],
    cmake_source_dir="../../"
)
