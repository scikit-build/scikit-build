from skbuild import setup

setup(
    name="pen2_cython",
    version="0.0.1",
    description="double pendulum simulation (cython version)",
    author="The scikit-build team",
    license="MIT",

    packages=['pen2_cython'],
    package_dir={
        'pen2_cython': 'src'
    },
    scripts=['scripts/pen2_cython']
)
