#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = list(filter(bool, (
    line.strip() for line in open('requirements.txt'))))

dev_requirements = list(filter(bool, (
    line.strip() for line in open('requirements-dev.txt'))))

setup(
    name='scikit-build',
    version='0.1.0',
    description='Simplify building Python extensions with CMake',
    long_description=readme + '\n\n' + history,
    author='the scikit-build team',
    author_email='scikit-build@googlegroups.com',
    url='https://github.com/scikit-build/scikit-build',
    packages=['skbuild', 'skbuild.platform_specifics'],
    package_dir={'skbuild': 'skbuild',
                 'skbuild.platform_specifics': 'skbuild/platform_specifics'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords='scikit-build',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=dev_requirements
)
