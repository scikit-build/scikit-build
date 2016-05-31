from skbuild import setup

requirements = list(filter(bool, (
    line.strip() for line in open('requirements.txt'))))

dev_requirements = list(filter(bool, (
    line.strip() for line in open('requirements-dev.txt'))))

setup(
    name="tower_of_babel",
    version="0.0.1",
    description="integration test of skbuild's support across various python"
                "module types and code generation technologies",
    author="skbuild team",
    license="MIT",

    install_requires=requirements,
    tests_require=dev_requirements,

    py_modules=['tbabel_python'],
    scripts=['scripts/tbabel'],
)

