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

# TODO: put package requirements here
requirements = []

# TODO: put package test requirements here
test_requirements = ["nose", ]

setup(
    name='PyCMake',
    version='0.1.0',
    description='Simplify building Python extensions with CMake',
    long_description=readme + '\n\n' + history,
    author='PyCMake team',
    author_email='pycmake@googlegroups.com',
    url='https://github.com/PyCMake/PyCMake',
    packages=['pycmake', 'pycmake.platform_specifics'],
    package_dir={'pycmake': 'pycmake', 
                 'pycmake.platform_specifics': 'pycmake/platform_specifics'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords='PyCMake',
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
    tests_require=test_requirements
    )
