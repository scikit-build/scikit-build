from skbuild import setup

setup(
    name="hello",
    version="1.2.3",
    description=(
        "a minimal example packagze that should always fail to build "
        "because it provides a _hello.cxx with a compile error"
    ),
    author="The scikit-build team",
    license="MIT",
    packages=["hello"],
)
