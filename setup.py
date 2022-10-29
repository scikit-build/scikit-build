#!/usr/bin/env python

import setuptools

# Produce an ImportError if this is missing
import setuptools_scm  # noqa: F401

with open("README.rst") as fp:
    readme = fp.read()

with open("HISTORY.rst") as fp:
    history = fp.read().replace(".. :changelog:", "")

with open("requirements.txt") as fp:
    requirements = list(filter(bool, (line.strip() for line in fp)))

with open("requirements-dev.txt") as fp:
    dev_requirements = list(filter(bool, (line.strip() for line in fp)))

with open("requirements-docs.txt") as fp:
    doc_requirements = list(filter(bool, (line.strip() for line in fp)))

setuptools.setup(
    name="scikit-build",
    description="Improved build system generator for Python C/C++/Fortran/Cython extensions",
    long_description_content_type="text/x-rst; charset=UTF-8",
    long_description=readme + "\n\n" + history,
    author="The scikit-build team",
    author_email="scikit-build@googlegroups.com",
    url="https://github.com/scikit-build/scikit-build",
    packages=setuptools.find_packages(include=["skbuild*"]),
    project_urls={
        "Documentation": "https://scikit-build.readthedocs.io/",
        "Bug Tracker": "https://github.com/scikit-build/scikit-build/issues",
        "Changelog": "https://scikit-build.readthedocs.io/en/latest/changes.html",
        "Mailing List": "https://groups.google.com/forum/#!forum/scikit-build",
        "Examples": "https://github.com/scikit-build/scikit-build-sample-projects",
    },
    package_data={"skbuild": ["resources/cmake/*.cmake", "py.typed", "*.pyi"]},
    python_requires=">=3.6",
    install_requires=requirements,
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
    extras_require={"test": dev_requirements, "docs": doc_requirements},
)
