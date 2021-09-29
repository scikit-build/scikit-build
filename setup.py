#!/usr/bin/env python
# -*- coding: utf-8 -*-

import versioneer

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
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Improved build system generator for Python C/C++/Fortran/Cython extensions',
    long_description_content_type='text/x-rst; charset=UTF-8',
    long_description=readme + '\n\n' + history,
    author='The scikit-build team',
    author_email='scikit-build@googlegroups.com',
    url='https://github.com/scikit-build/scikit-build',
    packages=[
        'skbuild',
        'skbuild.command',
        'skbuild.platform_specifics',
        'skbuild.utils'
    ],
    package_dir={'skbuild': 'skbuild',
                 'skbuild.platform_specifics': 'skbuild/platform_specifics',
                 'skbuild.command': 'skbuild/command'},
    project_urls={
        "Documentation": "https://scikit-build.readthedocs.io/",
        "Bug Tracker": "https://github.com/scikit-build/scikit-build/issues",
        "Changelog": "https://scikit-build.readthedocs.io/en/latest/changes.html",
        "Mailing List": "https://groups.google.com/forum/#!forum/scikit-build",
        "Examples": "https://github.com/scikit-build/scikit-build-sample-projects",
    },
    package_data={'skbuild': ['resources/cmake/*.cmake']},
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
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    extras_require={"test": dev_requirements},
)
