#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_utils
------------------------

Tests for utils functions.
"""

import os

saved_cwd = os.getcwd()


def setup_module():
    """ setup any state specific to the execution of the given module."""
    os.chdir(os.path.dirname(__file__))


def teardown_module():
    """ teardown any state that was previously setup with a setup_module
    method.
    """
    os.chdir(saved_cwd)


def test_push_dir():
    assert os.path.split(os.getcwd())[-1] == 'tests'

    from skbuild.utils import push_dir

    # No directory
    with push_dir():
        os.chdir(os.path.join(os.getcwd(), '..'))
        assert os.path.split(os.getcwd())[-1] == 'scikit-build'
    assert os.path.split(os.getcwd())[-1] == 'tests'

    # With directory
    with push_dir(directory=os.path.join(os.getcwd(), '..')):
        assert os.path.split(os.getcwd())[-1] == 'scikit-build'
    assert os.path.split(os.getcwd())[-1] == 'tests'
