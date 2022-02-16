from skbuild import setup

setup(
    name="hello",
    version="1.2.3",
    description="a minimal example package",
    author="The scikit-build team",
    license="MIT",
    packages=["bonjour", "hello"],
    package_data={"bonjour": ["data/*.txt", "data/terre.txt"]},
    py_modules=["bonjourModule", "helloModule"],
)
