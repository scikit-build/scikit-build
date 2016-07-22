from skbuild import setup

setup(
    name="root-package",
    version="1.2.3",
    description="a package that populates the root (nameless) package",
    author='The scikit-build team',
    license="MIT",
    package_dir={'': 'lib'},
    py_modules=['hello']
)
