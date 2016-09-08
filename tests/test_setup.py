#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_setup
----------------------------------

Tests for `skbuild.setup` function.
"""

from distutils.core import Distribution as distutils_Distribution
from setuptools import Distribution as setuptool_Distribution

from skbuild import setup as skbuild_setup

from . import push_argv


def test_distribution_object():

    with push_argv(["setup.py", "--name"]):
        distribution = skbuild_setup(
            name="test_distribution_type",
            version="0.0.1",
            description=(
                "test object returned by setup function"),
            author="The scikit-build team",
            license="MIT",
        )
        assert issubclass(distribution.__class__,
                          (distutils_Distribution, setuptool_Distribution))

        assert not distribution.is_pure()
