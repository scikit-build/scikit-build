from skbuild import setup

setup(
    name="tower_of_babel",
    version="0.0.1",
    description="integration test of skbuild's support across various python"
                "module types and code generation technologies",
    author="skbuild team",
    license="MIT",

    scripts=['scripts/tbabel'],
)

