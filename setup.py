#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst', 'r') as fp:
    readme = fp.read()
with open('HISTORY.rst', 'r') as fp:
    history = fp.read().replace('.. :changelog:', '')

with open('requirements.txt', 'r') as fp:
    requirements = list(filter(bool, (line.strip() for line in fp)))

with open('requirements-dev.txt', 'r') as fp:
    dev_requirements = list(filter(bool, (line.strip() for line in fp)))

setup(
    name='scikit-build',
    version='0.1.0',
    description='Improved build system generator for Python C extensions',
    long_description=readme + '\n\n' + history,
    author='The scikit-build team',
    author_email='scikit-build@googlegroups.com',
    url='https://github.com/scikit-build/scikit-build',
    packages=['skbuild', 'skbuild.platform_specifics', 'skbuild.command'],
    package_dir={'skbuild': 'skbuild',
                 'skbuild.platform_specifics': 'skbuild/platform_specifics',
                 'skbuild.command': 'skbuild/command'},
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
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=dev_requirements
)
