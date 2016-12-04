#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""test_command_line
----------------------------------

Tests for various command line functionality.
"""

import os
import pytest

from skbuild.utils import push_dir, to_platform_path

from . import project_setup_py_test


@project_setup_py_test("hello", ["--help"])
def test_help(capsys):
    out, err = capsys.readouterr()
    assert "scikit-build options" not in out
    assert "Global options:" in out
    assert "usage:" in out


@project_setup_py_test("hello", ["--help-commands"])
def test_help_commands(capsys):
    out, err = capsys.readouterr()
    assert "scikit-build options" in out
    assert "--build-type" in out
    assert "Global options:" not in out
    assert "usage:" in out


@project_setup_py_test("hello", ["--author", "--name"])
def test_metadata_display(capsys):
    out, err = capsys.readouterr()
    assert "scikit-build options" not in out
    assert "Global options:" not in out
    assert "usage:" not in out
    assert "The scikit-build team" == out.splitlines()[0]
    assert "hello" == out.splitlines()[1]


def test_no_command():
    with push_dir():

        @project_setup_py_test("hello", [])
        def run():
            pass

        failed = False
        try:
            run()
        except SystemExit as e:
            failed = 'error: no commands supplied' in e.args[0]

        assert failed
        assert not os.path.exists('_skbuild')


def test_invalid_command():

    with push_dir():

        @project_setup_py_test("hello", ["unknown"])
        def run():
            pass

        failed = False
        try:
            run()
        except SystemExit as e:
            failed = 'error: invalid command' in e.args[0]

        assert failed
        assert not os.path.exists('_skbuild')


def test_too_many_separators():
    with push_dir():

        @project_setup_py_test("hello", ["--"] * 3)
        def run():
            pass

        failed = False
        try:
            run()
        except SystemExit as e:
            failed = e.args[0].startswith('ERROR: Too many')

        assert failed


@project_setup_py_test("hello",
                       ["build", "--", "-DMY_CMAKE_VARIABLE:BOOL=1"])
def test_cmake_args(capfd):
    out, err = capfd.readouterr()
    assert "Manually-specified variables were not used by the project" in err
    assert "MY_CMAKE_VARIABLE" in err


@pytest.mark.parametrize("action", ['sdist', 'bdist_wheel'])
@pytest.mark.parametrize("hide_listing", [True, False])
def test_sdist_hide_listing(action, hide_listing, capfd):

    cmd = [action, "--", "-DMY_CMAKE_VARIABLE:BOOL=1"]
    if hide_listing:
        cmd.insert(0, "--hide-listing")

    @project_setup_py_test("hello", cmd, verbose_git=False)
    def run():
        pass

    run()

    out, _ = capfd.readouterr()
    if hide_listing:
        assert to_platform_path("bonjour/__init__.py") not in out
    else:
        assert to_platform_path("bonjour/__init__.py") in out

    if action == "sdist":
        what = "copied"
        if hasattr(os, 'link'):
            what = "hard-linked"
        assert "%s 7 files" % what in out
    elif action == "bdist_wheel":
        assert "copied 4 files" in out  # build_py
        assert "copied 5 files" in out  # install_lib
        assert "copied 0 files" in out  # install_scripts


@project_setup_py_test("hello", ["--force-cmake", "--help"])
def test_run_cmake_arg(capfd):
    out, _ = capfd.readouterr()
    assert "Generating done" in out


@project_setup_py_test("hello", ["--skip-cmake", "build"])
def test_skip_cmake_arg(capfd):
    out, _ = capfd.readouterr()
    assert "Generating done" not in out
