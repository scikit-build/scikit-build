#!/usr/bin/env python

import setuptools

# Produce an ImportError if this is missing
import setuptools_scm  # noqa: F401

with open("README.rst") as fp:
    readme = fp.read()

with open("HISTORY.rst") as fp:
    history = fp.read().replace(".. :changelog:", "")

extras_require = {
    "test": [
        "build>=0.7",
        "cython>=0.25.1",
        'importlib-metadata;python_version<"3.8"',
        "pytest>=6.0.0",
        "pytest-mock>=1.10.4",
        "pytest-virtualenv>=1.2.5",
        "requests",
        "virtualenv",
    ],
    "doctest": [
        "ubelt >= 0.8.2",
        "xdoctest>=0.10.0",
    ],
    "cov": [
        "codecov>=2.0.5",
        "coverage>=4.2",
        "pytest-cov>=2.7.1",
    ],
    "docs": [
        "pygments",
        "sphinx>=4",
        "sphinx-issues",
        "sphinx-rtd-theme>=1.0",
        "sphinxcontrib-moderncmakedomain>=3.19",
    ],
}


setuptools.setup(
    name="scikit-build",
    description="Improved build system generator for Python C/C++/Fortran/Cython extensions",
    long_description_content_type="text/x-rst; charset=UTF-8",
    long_description=readme + "\n\n" + history,
    author="The scikit-build team",
    url="https://github.com/scikit-build/scikit-build",
    packages=setuptools.find_packages(include=["skbuild*"]),
    project_urls={
        "Documentation": "https://scikit-build.readthedocs.io/",
        "Bug Tracker": "https://github.com/scikit-build/scikit-build/issues",
        "Changelog": "https://scikit-build.readthedocs.io/en/latest/changes.html",
        "Discussions": "https://github.com/orgs/scikit-build/discussions",
        "Examples": "https://github.com/scikit-build/scikit-build-sample-projects",
    },
    package_data={"skbuild": ["resources/cmake/*.cmake", "py.typed", "*.pyi"]},
    python_requires=">=3.6",
    install_requires=[
        "distro",
        "packaging",
        "setuptools>=42.0.0",
        'typing-extensions>=3.7; python_version < "3.8"',
        "wheel>=0.32.0",
    ],
    license="MIT",
    zip_safe=False,
    keywords="scikit-build",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
    ],
    extras_require=extras_require,
)
