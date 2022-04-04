import sys

try:
    import skbuild
    from skbuild import setup
except ImportError:
    print(
        "Please update pip, you need pip 10 or greater,\n"
        " or you need to install the PEP 518 requirements in pyproject.toml yourself",
        file=sys.stderr,
    )
    raise

print("Scikit-build version:", skbuild.__version__)


setup(
    name="hello-numpy",
    version="1.2.3",
    description="a minimal example package (with pybind11 and NumPy)",
    author="Hameer Abbasi",
    license="MIT",
    packages=["hello"],
    package_dir={"": "src"},
    install_requires=["numpy>=1.7"],
    cmake_install_dir="src/hello",
)
