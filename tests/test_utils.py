#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_utils
------------------------

Tests for utils functions.
"""

import os

from skbuild.utils import mkdir_p

saved_cwd = os.getcwd()


def setup_module():
    """ setup any state specific to the execution of the given module."""
    os.chdir(os.path.dirname(__file__))


def teardown_module():
    """ teardown any state that was previously setup with a setup_module
    method.
    """
    os.chdir(saved_cwd)


def test_push_dir(tmpdir):
    assert os.path.split(os.getcwd())[-1] == 'tests'

    from skbuild.utils import push_dir

    # No directory
    with push_dir():
        os.chdir(os.path.join(os.getcwd(), '..'))
        assert os.path.split(os.getcwd())[-1] == 'scikit-build'
    assert os.path.split(os.getcwd())[-1] == 'tests'

    # With existing directory
    with push_dir(directory=os.path.join(os.getcwd(), '..')):
        assert os.path.split(os.getcwd())[-1] == 'scikit-build'
    assert os.path.split(os.getcwd())[-1] == 'tests'

    foo_directory = os.path.join(str(tmpdir), 'foo')

    # With non existing directory
    failed = False
    try:
        with push_dir(directory=foo_directory):
            pass
    except OSError:
        failed = True
    assert failed
    assert not os.path.isdir(foo_directory)

    # With make_directory option
    with push_dir(directory=foo_directory, make_directory=True):
        assert os.getcwd() == foo_directory
    assert os.path.split(os.getcwd())[-1] == 'tests'
    assert os.path.isdir(foo_directory)


def test_push_dir_decorator(tmpdir):
    assert os.path.split(os.getcwd())[-1] == 'tests'

    from skbuild.utils.decorator import push_dir

    # No directory
    @push_dir()
    def test_default():
        os.chdir(os.path.join(os.getcwd(), '..'))
        assert os.path.split(os.getcwd())[-1] == 'scikit-build'

    test_default()
    assert os.path.split(os.getcwd())[-1] == 'tests'

    # With existing directory
    @push_dir(directory=os.path.join(os.getcwd(), '..'))
    def test():
        assert os.path.split(os.getcwd())[-1] == 'scikit-build'

    test()
    assert os.path.split(os.getcwd())[-1] == 'tests'

    foo_directory = os.path.join(str(tmpdir), 'foo')

    # With non existing directory
    failed = False
    try:
        @push_dir(directory=foo_directory)
        def test():
            pass

        test()
    except OSError:
        failed = True
    assert failed
    assert not os.path.isdir(foo_directory)

    # With make_directory option
    @push_dir(directory=foo_directory, make_directory=True)
    def test():
        assert os.getcwd() == foo_directory

    test()
    assert os.path.split(os.getcwd())[-1] == 'tests'
    assert os.path.isdir(foo_directory)


def test_mkdir_p(tmpdir):
    tmp_dir = str(tmpdir)
    assert os.path.isdir(tmp_dir)

    foo_bar_dir = os.path.join(tmp_dir, 'foo', 'bar')

    mkdir_p(foo_bar_dir)
    assert os.path.isdir(foo_bar_dir)

    # Make sure calling function twice does not raise an exception
    mkdir_p(foo_bar_dir)
    assert os.path.isdir(foo_bar_dir)
