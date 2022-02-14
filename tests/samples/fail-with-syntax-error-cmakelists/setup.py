from skbuild import setup

setup(
    name="fail_with_syntax_error_cmakelists",
    version="0.0.1",
    description=(
        "test project that should always fail to build because it " "provides a CMakeLists.txt with a syntax error"
    ),
    author="The scikit-build team",
    license="MIT",
)
