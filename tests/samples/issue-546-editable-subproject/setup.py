# failing case
from skbuild import setup

setup(
    name="example_package",
    packages=["example", "example.tools"],
    package_dir={"": "src"}
)
