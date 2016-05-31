from skbuild import setup

requirements = list(filter(bool, (
    line.strip() for line in open('requirements.txt'))))

dev_requirements = list(filter(bool, (
    line.strip() for line in open('requirements-dev.txt'))))

setup(
    name="pen2_cython",
    version="0.0.1",
    description="double pendulum simulation (cython version)",
    author="skbuild team",
    license="MIT",

    install_requires=requirements,
    tests_require=dev_requirements,

    packages=['pen2_cython'],
    package_dir={
        'pen2_cython': 'src'
    },
    scripts=['scripts/pen2_cython']
)
